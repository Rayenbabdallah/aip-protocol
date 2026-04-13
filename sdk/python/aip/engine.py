"""
PactEngine

The state machine that enforces the AIP lifecycle.
Bid -> (Echo cycles, bounded) -> Pact -> Flow -> Seal or Drift
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4

from aip.primitives import Bid, Drift, Echo, Pact, PactState, Seal, Spun, Yield


class AIPViolation(Exception):
    """
    Exception raised when the fundamental rules of AIP are violated.
    """

    def __init__(self, message: str, violation_type: str):
        super().__init__(message)
        self.violation_type = violation_type


class PactEngine:
    """
    The enforcement layer for AIP.
    Ensures work takes time, resolves definitively, and follows its constraints.
    """

    def __init__(self):
        # Memory of all Pacts currently being worked on
        self.active_pacts: dict[UUID, Pact] = {}
        self.pact_states: dict[UUID, PactState] = {}
        # Track echo haggling cycles per originating bid
        self.echo_counts: dict[UUID, int] = {}

    def _log(self, action: str, entity_id: UUID, message: str) -> None:
        """Internal audit log. Timestamps the lifecycle of agent work."""
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[{ts}] {action.upper()} ({entity_id}) | {message}")

    async def bid(
        self, from_agent: str, to_agent: str, intent: dict[str, Any], constraints: dict[str, Any]
    ) -> Bid:
        """
        Initiates the gesture. Neither committed nor flowing yet.
        """
        bid_id = uuid4()
        b = Bid(bid_id, from_agent, to_agent, intent, constraints)
        self.echo_counts[bid_id] = 0
        self._log("bid_initiated", bid_id, f"{from_agent} -> {to_agent}")
        return b

    async def echo(
        self,
        original_bid: Bid,
        modified_intent: dict[str, Any],
        modified_constraints: dict[str, Any],
        message: str,
    ) -> Echo:
        """
        Reshapes the terms. Boundaries are checked to prevent endless haggling.
        """
        limit = original_bid.constraints.get("echo_limit", 3)
        count = self.echo_counts.get(original_bid.bid_id, 0)

        if count >= limit:
            self._log("echo_violation", original_bid.bid_id, f"Limit of {limit} reached")
            raise AIPViolation(f"Echo limit of {limit} reached", "ECHO_LIMIT_EXCEEDED")

        self.echo_counts[original_bid.bid_id] = count + 1
        echo_id = uuid4()
        e = Echo(
            echo_id=echo_id,
            original_bid_id=original_bid.bid_id,
            from_agent=original_bid.to_agent,  # roles flip softly during negotiation
            to_agent=original_bid.from_agent,
            modified_intent=modified_intent,
            modified_constraints=modified_constraints,
            message=message,
        )
        self._log(
            "echo_emitted", echo_id, f"Iteration {count + 1} for bid {original_bid.bid_id}"
        )
        return e

    async def form_pact(self, bid: Bid) -> Pact:
        """
        Called when terms converge. Turns a loose gesture into a bonded Pact.
        """
        pact_id = uuid4()
        p = Pact(
            pact_id=pact_id,
            bid=bid,
            initiator=bid.from_agent,
            receiver=bid.to_agent,
            depth=0,
        )
        self.active_pacts[pact_id] = p
        self.pact_states[pact_id] = PactState.COMMITTED
        self._log("pact_formed", pact_id, "Convergence achieved")
        return p

    async def flow(self, pact: Pact, handler: Callable) -> Yield | Drift:
        """
        Executes the pact. Time and cost are actively measured here.
        Every flow must resolve into Seal or Drift.
        """
        if pact.pact_id not in self.active_pacts:
            raise AIPViolation("Pact not found or not formed", "PACT_NOT_FOUND")

        current_state = self.pact_states.get(pact.pact_id)
        if current_state != PactState.COMMITTED:
            raise AIPViolation(
                f"Pact cannot enter flow from state {current_state}",
                "INVALID_STATE_TRANSITION",
            )

        self.pact_states[pact.pact_id] = PactState.FLOWING
        self._log("flow_started", pact.pact_id, "Pact in motion")

        deadline = pact.bid.constraints.get("deadline", None)

        try:
            if deadline is not None and isinstance(deadline, (int, float)):
                # Deadline treated as a hard ceiling for timeout (in seconds)
                result = await asyncio.wait_for(handler(pact), timeout=float(deadline))
            else:
                result = await handler(pact)

            if isinstance(result, Yield):
                return result
            elif isinstance(result, Drift):
                return result
            else:
                raise AIPViolation(
                    "Handler must explicitly return a Yield or Drift", "INVALID_FLOW_OUTPUT"
                )

        except asyncio.TimeoutError:
            self._log(
                "deadline_violation", pact.pact_id, "Flow exceeded deadline constraint"
            )
            return await self.drift(
                pact, "Deadline constraint violated", ["TimeoutError during execution"]
            )
        except AIPViolation as e:
            # Trap constraint violations (like budget/depth) triggered inside the flow
            return await self.drift(pact, f"AIP Violation: {e.violation_type}", [str(e)])
        except Exception as e:
            self._log("flow_exception", pact.pact_id, str(e))
            return await self.drift(
                pact, f"Unhandled execution failure: {str(e)}", [str(e)]
            )

    async def seal(
        self,
        pact: Pact,
        output: Any,
        confidence: float,
        trace: list[Any],
        cost: float,
        spun_yields: list[Yield] | None = None,
    ) -> Yield:
        """
        The honored closure of a Pact. Evaluates the work against its constraints.
        """
        if confidence < 0.0 or confidence > 1.0:
            raise AIPViolation(
                "Confidence must be a true score between 0.0 and 1.0", "INVALID_CONFIDENCE"
            )

        if not trace:
            raise AIPViolation("A Sealed Pact must produce a trace", "MISSING_TRACE")

        budget = pact.bid.constraints.get("budget", float("inf"))
        if cost > budget:
            self._log(
                "budget_violation", pact.pact_id, f"Cost {cost} exceeded budget {budget}"
            )
            raise AIPViolation(
                f"Seal failed: Cost {cost} exceeds budget {budget}", "BUDGET_EXCEEDED"
            )

        spun_yields = spun_yields or []
        y = Yield(
            output=output,
            confidence=confidence,
            trace=trace,
            cost=cost,
            spun_yields=spun_yields,
        )

        self.pact_states[pact.pact_id] = PactState.SEALED
        if pact.pact_id in self.active_pacts:
            del self.active_pacts[pact.pact_id]

        self._log("pact_sealed", pact.pact_id, f"Honored with confidence {confidence}")
        return y

    async def drift(self, pact: Pact, reason: str, trace: list[Any]) -> Drift:
        """
        The graceful fracturing of a Pact. Drift is not dead execution; it is information.
        """
        if not trace:
            raise AIPViolation("A Drifted Pact must produce a trace", "MISSING_TRACE")

        d = Drift(reason=reason, trace=trace, depth=pact.depth)

        self.pact_states[pact.pact_id] = PactState.DRIFTED
        if pact.pact_id in self.active_pacts:
            del self.active_pacts[pact.pact_id]

        self._log("pact_drifted", pact.pact_id, reason)
        return d

    async def spin(
        self, parent_pact: Pact, intent: dict[str, Any], constraints: dict[str, Any]
    ) -> Pact:
        """
        Delegation. A child Pact forms internally from within an existing Flow.
        """
        limit = parent_pact.bid.constraints.get("depth_limit", 1)
        new_depth = parent_pact.depth + 1

        if new_depth > limit:
            self._log(
                "depth_violation", parent_pact.pact_id, f"Depth {new_depth} exceeds limit {limit}"
            )
            raise AIPViolation(f"Depth limit {limit} reached", "DEPTH_LIMIT_EXCEEDED")

        child_bid_id = uuid4()
        to_agent = constraints.get("to_agent", "UNKNOWN_DELEGATE")

        child_bid = Bid(
            bid_id=child_bid_id,
            from_agent=parent_pact.receiver,
            to_agent=to_agent,
            intent=intent,
            constraints=constraints,
        )

        child_pact_id = uuid4()
        child_pact = Pact(
            pact_id=child_pact_id,
            bid=child_bid,
            initiator=parent_pact.receiver,
            receiver=to_agent,
            depth=new_depth,
            parent_pact_id=parent_pact.pact_id,
        )

        self.active_pacts[child_pact_id] = child_pact
        self.pact_states[child_pact_id] = PactState.COMMITTED
        self._log(
            "pact_spun",
            child_pact_id,
            f"Delegation depth {new_depth} originated from {parent_pact.pact_id}",
        )

        return child_pact
