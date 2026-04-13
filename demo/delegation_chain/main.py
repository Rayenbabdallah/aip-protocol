import asyncio
import sys
from pathlib import Path

# Grant local script immediate access to the internal AIP SDK structure natively
sdk_path = Path(__file__).resolve().parent.parent.parent / "sdk" / "python"
sys.path.insert(0, str(sdk_path))

from aip import AgentRegistry, LocalTransport, PactEngine
from agents import log_transition, setup_agents


async def main():
    engine = PactEngine()
    transport = LocalTransport()
    registry = AgentRegistry()
    
    # Silence the strict internal audit logs so the pristine CLI formatting commands attention natively
    engine._log = lambda *args, **kwargs: None
    transport._log = lambda *args, **kwargs: None
    
    coordinator, researcher, writer = setup_agents(registry, engine, transport)
    
    # Phase 1: Initiation
    intent = {"task": "Research AI agent frameworks"}
    constraints = {"budget": 10.0, "deadline": 30.0, "depth_limit": 2, "echo_limit": 2}
    
    # Send bid starts the interaction/haggle loop natively
    pact_ab = await coordinator.send_bid(to_agent="researcher", intent=intent, constraints=constraints)
    
    if hasattr(pact_ab, 'reason'):
        print(f"Failed to converge. Drifted: {pact_ab.reason}")
        return
        
    pid_short = str(pact_ab.pact_id)[:8]
    log_transition("PACT", f"coordinator ↔ researcher: pact_{pid_short} formed")
    log_transition("FLOW", f"pact_{pid_short} in motion...")
    
    
    # Phase 2: Flow Execution Map
    async def run_research_flow(pact):
        await asyncio.sleep(1.0)
        
        # Mid-flow delegation fracture!
        sub_intent = {"task": "Summarize these findings into 3 key insights"}
        pact_bc = await researcher.spawn(pact, "writer", sub_intent)
        
        async def run_write_flow(child_pact):
            await asyncio.sleep(0.8)
            return await engine.seal(
                pact=child_pact,
                output=["1. Agents need memory", "2. Protocols matter", "3. Pacts > APIs"],
                confidence=0.85,
                trace=["Processed RAW text into 3 insights"],
                cost=1.5
            )
            
        child_yield = await engine.flow(pact_bc, run_write_flow)
        
        cid_short = str(pact_bc.pact_id)[:8]
        log_transition("SEAL", f"pact_{cid_short} sealed | confidence: {child_yield.confidence}")
        
        return await engine.seal(
            pact=pact,
            output="Comprehensive AI Agent report generated",
            confidence=0.91,
            trace=["Scanned endpoints", "Delegated formatting", "Finalized scope structured output"],
            cost=4.8,
            spun_yields=[child_yield]
        )
        
    final_yield = await engine.flow(pact_ab, run_research_flow)
    
    log_transition("SEAL", f"pact_{pid_short} sealed | confidence: {final_yield.confidence}")
    log_transition("YIELD", "coordinator received final output")


if __name__ == "__main__":
    asyncio.run(main())
