"""
AIP Transport Layer.

The invisible nerve system mapping Bids, Echos, and Yields across physical or async spaces.
It is silent when it works, and loud when it breaks.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

from aip.agent import Agent
from aip.engine import AIPViolation
from aip.primitives import Bid, Echo, Yield


class BaseTransport:
    """Provides common logging primitives for all strict transporting logic."""

    def _log(self, direction: str, msg_type: str, from_id: str, to_id: str, detail: str = "") -> None:
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[{ts}] TRANSPORT_{direction.upper()} | {msg_type} | {from_id} -> {to_id} | {detail}")


class LocalTransport(BaseTransport):
    """
    Agents in the same process communicate directly via method invocation.
    Execution blocks the logical flow context synchronously in the asyncio loop.
    """

    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def connect(self, *agents: Agent) -> None:
        """Bind one or multiple Agents intrinsically to the transport topology."""
        for a in agents:
            self._agents[a.id] = a

    def _get_target(self, to_agent: str) -> Agent:
        if to_agent not in self._agents:
            raise AIPViolation(f"Agent {to_agent} is unknown to transport layer", "UNKNOWN_AGENT")
        return self._agents[to_agent]

    async def send_bid(self, bid: Bid) -> Any:
        self._log("send", "BID", bid.from_agent, bid.to_agent, str(bid.bid_id))
        target = self._get_target(bid.to_agent)
        deadline = bid.constraints.get("deadline", None)

        handler = target._bid_handler
        if not handler:
            return "refuse"

        try:
            if deadline is not None and isinstance(deadline, (int, float)):
                return await asyncio.wait_for(handler(bid), timeout=float(deadline))
            return await handler(bid)
        except asyncio.TimeoutError:
            self._log("fail", "BID", bid.from_agent, bid.to_agent, f"Deadline {deadline} exceeded")
            raise AIPViolation(f"Bid expired. Target {bid.to_agent} missed deadline.", "TIMEOUT")

    async def send_echo(self, echo: Echo) -> Any:
        self._log("send", "ECHO", echo.from_agent, echo.to_agent, str(echo.echo_id))
        target = self._get_target(echo.to_agent)
        deadline = echo.modified_constraints.get("deadline", None)

        handler = target._echo_handler
        if not handler:
            return "refuse"

        try:
            if deadline is not None and isinstance(deadline, (int, float)):
                return await asyncio.wait_for(handler(echo), timeout=float(deadline))
            return await handler(echo)
        except asyncio.TimeoutError:
            self._log("fail", "ECHO", echo.from_agent, echo.to_agent, f"Deadline {deadline} exceeded")
            raise AIPViolation(f"Echo expired. Target {echo.to_agent} missed deadline.", "TIMEOUT")

    async def send_yield(self, yield_: Yield) -> None:
        """
        Broadcasts the Yield across the process, leaving certainty.
        """
        cost_str = f"${yield_.cost}" if yield_.cost else "None"
        self._log("deliver", "YIELD", "seal", "system", f"Conf: {yield_.confidence} | Cost: {cost_str}")


class AsyncQueueTransport(BaseTransport):
    """
    Agents communicate via isolated asyncio queues.
    This simulates distributed network latency/queuing flows safely for parallel testing.
    """

    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._queues: dict[str, asyncio.Queue] = {}
        self._workers: list[asyncio.Task] = []

    def connect(self, *agents: Agent) -> None:
        for a in agents:
            self._agents[a.id] = a
            if a.id not in self._queues:
                self._queues[a.id] = asyncio.Queue()
                
                # Spin background coroutine reading messages for this specific agent
                task = asyncio.create_task(self._process_queue(a.id))
                self._workers.append(task)

    async def _process_queue(self, agent_id: str) -> None:
        agent = self._agents[agent_id]
        queue = self._queues[agent_id]

        while True:
            # Future architecture links async boundaries across the logical queue separation
            msg_type, msg, future, deadline = await queue.get()

            try:
                handler = agent._bid_handler if msg_type == "BID" else agent._echo_handler
                if not handler:
                    result = "refuse"
                else:
                    if deadline is not None and isinstance(deadline, (int, float)):
                        result = await asyncio.wait_for(handler(msg), timeout=float(deadline))
                    else:
                        result = await handler(msg)

                if not future.done():
                    future.set_result(result)

            except Exception as e:
                # Capture standard timeout or handler failures back down natively.
                if not future.done():
                    future.set_exception(e)
            finally:
                queue.task_done()

    def _get_target(self, to_agent: str) -> Agent:
        if to_agent not in self._agents:
            raise AIPViolation(f"Agent {to_agent} is unknown to transport layer", "UNKNOWN_AGENT")
        return self._agents[to_agent]

    async def send_bid(self, bid: Bid) -> Any:
        self._log("enqueue", "BID", bid.from_agent, bid.to_agent, str(bid.bid_id))
        target = self._get_target(bid.to_agent)
        deadline = bid.constraints.get("deadline", None)

        future = asyncio.Future()
        await self._queues[bid.to_agent].put(("BID", bid, future, deadline))

        try:
            # Transport forces timeout boundary constraints mapping onto the future retrieval
            if deadline is not None and isinstance(deadline, (int, float)):
                return await asyncio.wait_for(future, timeout=float(deadline) + 1.0)
            return await future
        except asyncio.TimeoutError:
            self._log("fail", "BID", bid.from_agent, bid.to_agent, "Deadline exceeded in transport queue")
            raise AIPViolation(f"Bid expired. Target {bid.to_agent} missed deadline.", "TIMEOUT")

    async def send_echo(self, echo: Echo) -> Any:
        self._log("enqueue", "ECHO", echo.from_agent, echo.to_agent, str(echo.echo_id))
        target = self._get_target(echo.to_agent)
        deadline = echo.modified_constraints.get("deadline", None)

        future = asyncio.Future()
        await self._queues[echo.to_agent].put(("ECHO", echo, future, deadline))

        try:
            if deadline is not None and isinstance(deadline, (int, float)):
                return await asyncio.wait_for(future, timeout=float(deadline) + 1.0)
            return await future
        except asyncio.TimeoutError:
            self._log("fail", "ECHO", echo.from_agent, echo.to_agent, "Deadline exceeded in transport queue")
            raise AIPViolation(f"Echo expired. Target {echo.to_agent} missed deadline.", "TIMEOUT")

    async def send_yield(self, yield_: Yield) -> None:
        cost_str = f"${yield_.cost}" if yield_.cost else "None"
        self._log("deliver", "YIELD", "seal", "system", f"Conf: {yield_.confidence} | Cost: {cost_str}")
