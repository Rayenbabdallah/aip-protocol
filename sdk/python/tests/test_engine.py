import pytest
import asyncio
from typing import Any
from aip import PactEngine, Agent, AgentRegistry, LocalTransport

@pytest.mark.asyncio
async def test_budget_exceeded_triggers_drift():
    """Validates structural seal rejection automatically cascades seamlessly natively into a trace Drift."""
    engine = PactEngine()
    engine._log = lambda *args, **kwargs: None
    registry = AgentRegistry()
    transport = LocalTransport()
    
    a1 = Agent("initiator", [], engine=engine, registry=registry, transport=transport)
    a2 = Agent("receiver", [], engine=engine, registry=registry, transport=transport)
    registry.register(a1)
    registry.register(a2)
    transport.connect(a1, a2)
    
    @a2.on_bid
    async def accept_bid(bid):
        return None
    
    pact = await a1.send_bid("receiver", {}, {"budget": 10.0})
    
    async def working_flow(p):
        # Trigger explicit budget rupture safely tracking
        return await engine.seal(p, output="done", confidence=1.0, trace=["ran step 1"], cost=15.0)
        
    result = await engine.flow(pact, working_flow)
    assert hasattr(result, "reason")
    assert "BUDGET_EXCEEDED" in result.reason or "budget" in result.reason.lower()


@pytest.mark.asyncio
async def test_echo_limit_truncates_haggling():
    """Validates endless loops safely crack generating a logic fracture instead of hanging server bounds natively."""
    engine = PactEngine()
    engine._log = lambda *args, **kwargs: None
    registry = AgentRegistry()
    transport = LocalTransport()
    
    a1 = Agent("maker", [], engine=engine, registry=registry, transport=transport)
    a2 = Agent("taker", [], engine=engine, registry=registry, transport=transport)
    registry.register(a1)
    registry.register(a2)
    transport.connect(a1, a2)
    
    @a1.on_echo
    async def a1_echo(echo):
        # Bounce back
        return await engine.echo(echo, echo.modified_intent, echo.modified_constraints, "Haggle Step 1")
        
    @a2.on_bid
    async def a2_bid(bid):
        return await engine.echo(bid, bid.intent, bid.constraints, "Haggle Step 2")
        
    @a2.on_echo
    async def a2_echo(echo):
        return await engine.echo(echo, echo.modified_intent, echo.modified_constraints, "Haggle Step 3")

    result = await a1.send_bid("taker", {}, {"echo_limit": 2})
    assert hasattr(result, "reason")
    assert "ECHO_LIMIT_EXCEEDED" in " ".join(result.trace) or "Limit" in result.reason or "ECHO_LIMIT_EXCEEDED" in result.reason


@pytest.mark.asyncio
async def test_deadline_timeout_triggers_drift():
    """Validates engine explicitly wraps `wait_for` natively tracking functional limits securely seamlessly."""
    engine = PactEngine()
    engine._log = lambda *args, **kwargs: None
    registry = AgentRegistry()
    transport = LocalTransport()
    
    a1 = Agent("sender", [], engine=engine, registry=registry, transport=transport)
    a2 = Agent("worker", [], engine=engine, registry=registry, transport=transport)
    registry.register(a1)
    registry.register(a2)
    transport.connect(a1, a2)
    
    @a2.on_bid
    async def accept_bid(bid):
        return None
    
    pact = await a1.send_bid("worker", {}, {"deadline": 0.1})
    
    async def slow_flow(p):
        await asyncio.sleep(0.5)
        return await engine.seal(p, output="done", confidence=1.0, trace=["finished late"], cost=1.0)
        
    result = await engine.flow(pact, slow_flow)
    assert hasattr(result, "reason")
    assert "TimeoutError" in " ".join(result.trace)
