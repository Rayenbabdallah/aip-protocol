import asyncio
from typing import Any

from aip import Agent, AgentRegistry, Bid, Echo, LocalTransport, PactEngine


def log_transition(event: str, desc: str) -> None:
    """Renders a visually striking transition log mirroring a living system."""
    colors = {
        "BID": "\033[94m",   # Blue
        "ECHO": "\033[93m",  # Yellow
        "PACT": "\033[92m",  # Green
        "FLOW": "\033[96m",  # Cyan
        "SPIN": "\033[95m",  # Magenta
        "SEAL": "\033[92m",  # Green
        "YIELD": "\033[97m", # White
    }
    color = colors.get(event, "")
    reset = "\033[0m"
    print(f"{color}[{event:<5}]{reset}  {desc}")


def setup_agents(registry: AgentRegistry, engine: PactEngine, transport: LocalTransport):
    coordinator = Agent(id="coordinator", capabilities=["coordinate", "plan"], engine=engine, registry=registry, transport=transport)
    researcher = Agent(id="researcher", capabilities=["research", "analyze"], engine=engine, registry=registry, transport=transport)
    writer = Agent(id="writer", capabilities=["write", "summarize"], engine=engine, registry=registry, transport=transport)
    
    registry.register(coordinator)
    registry.register(researcher)
    registry.register(writer)
    
    # Wire the transport layer
    transport.connect(coordinator, researcher, writer)
    
    @coordinator.on_bid
    async def handle_coord_bid(bid: Bid):
        return None
        
    @coordinator.on_echo
    async def handle_coord_echo(echo: Echo):
        return None

    @researcher.on_bid
    async def handle_research_bid(bid: Bid):
        task_str = bid.intent.get('task', 'Unknown task')
        log_transition("BID", f"{bid.from_agent} → {bid.to_agent}: \"{task_str}\"")
        await asyncio.sleep(0.6) # simulate reasoning
        
        # Reject simple text scope, reshape the terms via Echo
        new_intent = dict(bid.intent)
        new_intent["output_format"] = "structured"
        message = "Scope adjusted to structured output"
        
        log_transition("ECHO", f"{bid.to_agent} → {bid.from_agent}: \"{message}\"")
        
        return await engine.echo(bid, new_intent, bid.constraints, message)
        
    @researcher.on_echo
    async def handle_research_echo(echo: Echo):
        return None

    @writer.on_bid
    async def handle_writer_bid(bid: Bid):
        log_transition("SPIN", f"{bid.from_agent} → {bid.to_agent}: child pact spawned")
        await asyncio.sleep(0.3)
        return None
        
    @writer.on_echo
    async def handle_writer_echo(echo: Echo):
        return None

    return coordinator, researcher, writer
