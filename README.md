# Agent Interaction Protocol (AIP)

Every API assumes blind submission; an intelligence must first agree to work.

AIP is an open standard designed to structure how autonomous systems negotiate, commit, and deliver outcomes mathematically. It abandons the naive foundations of stateless data exchange in favor of tracking physical work over time. Agents utilizing it do not merely call deterministic endpoints—they initiate bids, hammer out constraints natively, form strictly bonded pacts, and ultimately seal their commitments carrying confidence guarantees.

### The Delegation Chain
```python
pact_ab = await coordinator.send_bid("researcher", intent, constraints)

async def researcher_flow(pact):
    # Fracture work natively by spawning a child negotiation
    child_pact = await researcher.spawn(pact, "writer", {"task": "summarize"})
    child_yield = await engine.flow(child_pact, writer_logic)
    
    return await engine.seal(
        pact=pact,
        output="Comprehensive Report Created",
        confidence=0.91,
        trace=["Researched endpoints", "Delegated formatting"],
        cost=4.8,
        spun_yields=[child_yield]
    )

final_yield = await engine.flow(pact_ab, researcher_flow)
```

### The Eight Words
AIP’s nomenclature aligns strictly with the behavioral truth of agent interaction:

* **Bid** — The initiating gesture. One agent reaches toward another with intent.
* **Echo** — A Bid returning reshaped. Negotiation in motion. Intent preserved, terms changed.
* **Pact** — The atom of AIP. A mutual commitment formed when Bid and Echo converge.
* **Flow** — The active state of a Pact in physical motion over time.
* **Spun** — A child Pact born inside a parent Pact. Delegation is native.
* **Seal** — A Pact that honored its commitment, crystalized definitively into success.
* **Drift** — A Pact that could not hold, breaking gracefully and leaving a trace instead of silent failure.
* **Yield** — The verified output of a Sealed Pact, carrying confidence proofs, trace paths, and explicit costs.

### Installation
```bash
pip install aip-core
```

### Quickstart
```python
from aip import Agent, AgentRegistry, PactEngine, LocalTransport

engine, transport, registry = PactEngine(), LocalTransport(), AgentRegistry()

coord = Agent("coordinator", ["plan"], engine=engine, registry=registry)
worker = Agent("worker", ["execute"], engine=engine, registry=registry)

@worker.on_bid
async def execute_task(bid):
    return None # Silent consent guarantees compliance

registry.register(coord)
registry.register(worker)
transport.connect(coord, worker)

pact = await coord.send_bid("worker", {"task": "scan"}, {"budget": 5.0})
final = await engine.flow(pact, lambda p: engine.seal(p, output="Done", confidence=1.0, trace=["Scanned"], cost=0.1))
```

### Anatomy
* [spec/](spec/) - The technical protocol guidelines
* [sdk/python/](sdk/python/) - Python SDK and developer foundation
* [demo/](demo/) - Example chains covering primitives sequentially
* [docs/manifesto.md](docs/manifesto.md) - The philosophical underpinning marking the necessity of intent

AIP is an open protocol. Implement it. Break it. Improve it.
