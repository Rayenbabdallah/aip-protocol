"""
AIP Agent & Registry.

Agents are not tools with endpoints. They are workers with rights.
They haggle, they refuse, they agree, they work.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aip.primitives import Bid, Drift, Echo, Pact


class AgentRegistry:
    """
    An in-memory town square. 
    Where agents announce their presence and find others with the right skills to help.
    """

    def __init__(self):
        self.agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self.agents[agent.id] = agent

    def find(self, capability: str) -> list[Agent]:
        """Discover agents capable of a certain skill."""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def get(self, agent_id: str) -> Agent | None:
        return self.agents.get(agent_id)


class Agent:
    """
    The minimal functional interface for building AIP-compatible workers.
    An agent has capabilities, reputation, constraints, and the right to say no.
    """

    def __init__(
        self,
        id: str,
        capabilities: list[str],
        pricing: dict[str, Any] | None = None,
        reputation: float = 1.0,
        engine: Any = None,
        registry: AgentRegistry | None = None,
        transport: Any = None,
    ):
        self.id = id
        self.capabilities = capabilities
        self.pricing = pricing or {}
        self.reputation = reputation
        self.engine = engine
        self.registry = registry
        self.transport = transport

        # Async handlers for incoming interaction requests
        self._bid_handler: Callable[[Bid], Awaitable[Echo | str | None]] | None = None
        self._echo_handler: Callable[[Echo], Awaitable[Echo | str | None]] | None = None

    def on_bid(self, fn: Callable[[Bid], Awaitable[Echo | str | None]]) -> Callable:
        """Decorator to register what happens when this agent receives a fresh Bid."""
        self._bid_handler = fn
        return fn

    def on_echo(self, fn: Callable[[Echo], Awaitable[Echo | str | None]]) -> Callable:
        """Decorator to register what happens when a counter-proposal (Echo) arrives."""
        self._echo_handler = fn
        return fn

    async def _negotiate(self, to_agent: str, initial_bid: Bid) -> Bid | Drift:
        """
        The internal haggle loop. Routes inherently through the transport boundary ensuring
        queues, network delays, and latency constraints are properly trapped in AIP limits.
        """
        current_message = initial_bid
        current_receiver_id = to_agent
        current_sender_id = self.id
        is_first = True
        trace = [f"Negotiation opened between {self.id} and {to_agent}"]

        while True:
            try:
                if is_first:
                    response = await self.transport.send_bid(current_message)
                    is_first = False
                else:
                    response = await self.transport.send_echo(current_message)
            except Exception as e:
                trace.append(f"Negotiation collapsed due to exception/timeout: {e}")
                return Drift(f"Exception during negotiation: {e}", trace, 0)

            if response is None:
                # Silent consent = Accepted as-is
                trace.append(f"{current_receiver_id} accepted the terms silently.")
                if isinstance(current_message, Bid):
                    return current_message
                else:
                    # Echo accepted. We crystallize the agreed terms into a unified Bid structure.
                    return Bid(
                        bid_id=current_message.original_bid_id,
                        from_agent=self.id,  # Initiator acts as the originator of the final flow
                        to_agent=to_agent,
                        intent=current_message.modified_intent,
                        constraints=current_message.modified_constraints,
                    )
            elif isinstance(response, str) and response.lower() == "refuse":
                trace.append(f"{current_receiver_id} firmly refused.")
                return Drift("Agent refused the terms", trace, 0)
            elif isinstance(response, Echo):
                trace.append(f"{current_receiver_id} echoed back reshaped terms.")
                # Pass the hot potato back
                current_message = response
                current_receiver_id, current_sender_id = current_sender_id, current_receiver_id
            else:
                trace.append("Protocol breakdown: Invalid gesture format returned.")
                return Drift("Protocol violation", trace, 0)

    async def send_bid(
        self, to_agent: str, intent: dict[str, Any], constraints: dict[str, Any]
    ) -> Pact | Drift:
        """
        The act of reaching out to another agent with a proposal of work.
        """
        if not self.engine or not self.registry or not self.transport:
            raise RuntimeError(
                "Agent lacks existential reality (engine/registry/transport) to initiate work."
            )

        target = self.registry.get(to_agent)
        if not target:
            return Drift(
                f"Agent {to_agent} is nowhere to be found in the registry.",
                ["Registry Lookup Miss"],
                0,
            )

        initial_bid = await self.engine.bid(self.id, to_agent, intent, constraints)
        agreed_bid = await self._negotiate(to_agent, initial_bid)

        if isinstance(agreed_bid, Drift):
            return agreed_bid

        return await self.engine.form_pact(agreed_bid)

    async def spawn(
        self, parent_pact: Pact, to_agent: str, intent: dict[str, Any]
    ) -> Pact:
        """
        Delegation is native. A working agent requests a peer 
        to execute a subnet of its flow mid-execution, forming a Spun Pact.
        """
        if not self.engine or not self.registry or not self.transport:
            raise RuntimeError("Agent lacks the context to spawn child pacts.")

        target = self.registry.get(to_agent)
        if not target:
            raise RuntimeError(f"Target agent {to_agent} vanished or doesn't exist.")

        # Inherit strict limits securely from the parent constraints
        constraints = dict(parent_pact.bid.constraints)
        constraints["to_agent"] = to_agent

        initial_bid = await self.engine.bid(self.id, to_agent, intent, constraints)
        agreed_bid = await self._negotiate(to_agent, initial_bid)

        if isinstance(agreed_bid, Drift):
            raise RuntimeError(f"Spawn delegation was refused: {agreed_bid.reason}")

        return await self.engine.spin(
            parent_pact, agreed_bid.intent, agreed_bid.constraints
        )
