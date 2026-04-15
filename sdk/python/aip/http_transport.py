"""
AIP HTTP Transport.

Allows agents to physically break process boundaries tracking interactions natively across the web.
Requires `pip install agent-interaction-protocol[http]` (FastAPI + httpx).
"""

from typing import Any
from aip.agent import Agent
from aip.primitives import Bid, Echo, Yield
from aip.engine import AIPViolation
from aip.transport import BaseTransport

try:
    from fastapi import APIRouter, HTTPException
    import httpx
except ImportError:
    pass  # Rely on user catching this locally if they attempt invoking HTTP explicitly


class FastAPIEndpointTransport(BaseTransport):
    """
    Exposes an agent cleanly over HTTP natively. 
    Connects incoming web connections directly directly inside the Agent's handler securely.
    """
    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self.router = APIRouter()
        self._map_routes()

    def connect(self, *agents: Agent) -> None:
        for a in agents:
            self._agents[a.id] = a

    def _get_target(self, target_id: str) -> Agent:
        if target_id not in self._agents:
            raise HTTPException(status_code=404, detail="Agent unknown to this specific execution boundary endpoint")
        return self._agents[target_id]

    def _map_routes(self):
        @self.router.post("/aip/bid")
        async def receive_bid(bid_payload: dict):
            from uuid import UUID
            try:
                bid = Bid(
                    bid_id=UUID(bid_payload["bid_id"]),
                    from_agent=bid_payload["from_agent"],
                    to_agent=bid_payload["to_agent"],
                    intent=bid_payload["intent"],
                    constraints=bid_payload["constraints"]
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Structural Payload Failure natively: {e}")
            
            target = self._get_target(bid.to_agent)
            if not target._bid_handler: 
                return {"response": "refuse"}
            result = await target._bid_handler(bid)
            
            if result is None: 
                return {"response": "accept"}
            elif isinstance(result, str): 
                return {"response": "refuse"}
            elif isinstance(result, Echo): 
                return {
                    "response": "echo",
                    "echo_payload": {
                        "echo_id": str(result.echo_id),
                        "original_bid_id": str(result.original_bid_id),
                        "from_agent": result.from_agent,
                        "to_agent": result.to_agent,
                        "modified_intent": result.modified_intent,
                        "modified_constraints": result.modified_constraints,
                        "message": result.message
                    }
                }

        @self.router.post("/aip/echo")
        async def receive_echo(echo_payload: dict):
            from uuid import UUID
            try:
                echo = Echo(
                    echo_id=UUID(echo_payload["echo_id"]),
                    original_bid_id=UUID(echo_payload["original_bid_id"]),
                    from_agent=echo_payload["from_agent"],
                    to_agent=echo_payload["to_agent"],
                    modified_intent=echo_payload["modified_intent"],
                    modified_constraints=echo_payload["modified_constraints"],
                    message=echo_payload["message"]
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Structural Flow Failure: {e}")
                
            target = self._get_target(echo.to_agent)
            if not target._echo_handler: 
                return {"response": "refuse"}
            result = await target._echo_handler(echo)
            
            if result is None: 
                return {"response": "accept"}
            elif isinstance(result, str): 
                return {"response": "refuse"}
            elif isinstance(result, Echo): 
                return {
                    "response": "echo",
                    "echo_payload": {
                        "echo_id": str(result.echo_id),
                        "original_bid_id": str(result.original_bid_id),
                        "from_agent": result.from_agent,
                        "to_agent": result.to_agent,
                        "modified_intent": result.modified_intent,
                        "modified_constraints": result.modified_constraints,
                        "message": result.message
                    }
                }


class HttpClientTransport(BaseTransport):
    """
    Acts as the sender globally. Reaches across physical internet boundaries firing arrays inside remote agent routers securely!
    """
    def __init__(self, network_map: dict[str, str]):
        # Dynamic network map tracking exact endpoint resolutions (e.g. agent_map["bob"] = "https://server.domain.com")
        self.network_map = network_map

    async def _post(self, target_id: str, endpoint: str, payload: dict, timeout: float | None = 10.0):
        if target_id not in self.network_map:
            raise AIPViolation(f"Target {target_id} not explicitly documented organically mapping limits", "UNKNOWN_AGENT")
            
        url = f"{self.network_map[target_id]}/aip/{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                import asyncio
                res = await client.post(url, json=payload, timeout=timeout)
                res.raise_for_status()
                return res.json()
            except httpx.TimeoutException:
                raise AIPViolation("HTTP Execution network boundary exceeded limits flawlessly", "TIMEOUT")
            except httpx.HTTPError as e:
                raise AIPViolation(f"Explicit remote rupturing tracking dynamically natively: {e}", "NETWORK_FAULT")

    async def send_bid(self, bid: Bid) -> Any:
        self._log("transmit", "BID", bid.from_agent, bid.to_agent, str(bid.bid_id))
        payload = {
            "bid_id": str(bid.bid_id),
            "from_agent": bid.from_agent,
            "to_agent": bid.to_agent,
            "intent": bid.intent,
            "constraints": bid.constraints
        }
        deadline = bid.constraints.get("deadline", 10.0)
        
        reply = await self._post(bid.to_agent, "bid", payload, timeout=deadline)
        return self._parse_reply(reply)
        
    async def send_echo(self, echo: Echo) -> Any:
        self._log("transmit", "ECHO", echo.from_agent, echo.to_agent, str(echo.echo_id))
        payload = {
            "echo_id": str(echo.echo_id),
            "original_bid_id": str(echo.original_bid_id),
            "from_agent": echo.from_agent,
            "to_agent": echo.to_agent,
            "modified_intent": echo.modified_intent,
            "modified_constraints": echo.modified_constraints,
            "message": echo.message
        }
        deadline = echo.modified_constraints.get("deadline", 10.0)
        
        reply = await self._post(echo.to_agent, "echo", payload, timeout=deadline)
        return self._parse_reply(reply)
        
    def _parse_reply(self, reply: dict) -> Any:
        r = reply.get("response")
        if r == "accept": return None
        if r == "refuse": return "refuse"
        if r == "echo":
            data = reply["echo_payload"]
            from uuid import UUID
            return Echo(
                echo_id=UUID(data["echo_id"]),
                original_bid_id=UUID(data["original_bid_id"]),
                from_agent=data["from_agent"],
                to_agent=data["to_agent"],
                modified_intent=data["modified_intent"],
                modified_constraints=data["modified_constraints"],
                message=data["message"]
            )
        return "refuse"
