# AIP Python SDK

The official Python environment for building agents natively on the Agent Interaction Protocol.

## API Reference

The minimum viable stack mapping agent interaction requires three functional constructs: an `AgentRegistry` to map endpoints cleanly, a `PactEngine` enforcing strict constraint timelines securely over execution paths, and a `Transport` mapping communication borders physically.

### `Agent`
The fundamental worker class. Do not treat `Agent` classes like routing handlers; handle their intent boundaries carefully respecting they can deny logic loops organically natively via constraints.
```python
researcher = Agent(
    id="researcher", 
    capabilities=["research", "analyze"],
    engine=engine,
    registry=registry
)

@researcher.on_bid
async def handle_bid(bid: Bid):
    if not fits_internal_limits(bid.intent):
        return "refuse"  # Generates immediate Drift.
        
    return None  # Silently converges forming the standard Pact constraint.
```
- `agent.send_bid(...)` -> Triggers negotiations spanning `engine` and yields a working `Pact`.
- `agent.spawn(...)` -> Generates delegation boundaries recursively capturing constraints over mid-`flow()`.

### `PactEngine`
The state enforcement mechanism evaluating mathematical bounds mathematically inside memory constructs. Agents interface heavily with the pact engine utilizing tracking validation protocols automatically under the hood alongside standard lifecycle functions.
```python
await engine.form_pact(bid: Bid) -> Pact
await engine.flow(pact: Pact, handler: Callable) -> Yield | Drift
await engine.seal(pact: Pact, output: Any, confidence: float, trace: list, cost: float) -> Yield
await engine.drift(pact: Pact, reason: str, trace: list) -> Drift
await engine.spin(parent_pact: Pact, intent: dict, constraints: dict) -> Pact
```

### Transports
AIP abstracts connection mapping inside explicit functional transports routing Bids mapping over logical domains.
- **`LocalTransport`**: Extremely quick straightline sequential invocations isolating the connection bounds. Perfect for direct parallel testing securely isolated under a unified process tree.
- **`AsyncQueueTransport`**: Protects sequential domains across standard native queued boundaries routing isolation delays securely replicating distributed networking connections physically.

## Constraints Explained

Proper intelligent workflows structure explicitly formatted limitation keys spanning `Bid` dictionaries universally. Ensure you specify explicit limitation paths matching:
- **`budget`** _(float)_ → Enforced precisely within `.seal()`. Exceeded variables break constraint tracking catching an explicit `AIPViolation` and dropping gracefully into a drifted footprint locally.
- **`deadline`** _(float)_ → Measured via absolute execution seconds natively bridging `asyncio.wait_for`. Triggers standard asynchronous timeouts mapping into trace outputs naturally natively returning drifted context chains automatically.
- **`echo_limit`** _(int)_ → Truncates total bounds over how many cycles agents dynamically push modification values resolving endless haggle death natively avoiding execution stalls strictly tracking iteration depth bounds.
- **`depth_limit`** _(int)_ → The standard bounds placed recursively trapping the raw scale over what amount mid-routine executions instantiate `.spawn()` mapping.

## Explicit Error Handling
Avoid catching internal logic exceptions natively in loop boundaries resolving generic strings. Expect the formal `AIPViolation` whenever protocols tear functionally bypassing acceptable thresholds physically tracking logic mapping outputs precisely generating robust tracing endpoints!
```python
from aip.engine import AIPViolation

try:
    pact = await agent.send_bid("target", intent, constraints)
except AIPViolation as e:
    print(f"System boundary triggered: {e.violation_type}") # Ex: ECHO_LIMIT_EXCEEDED
```

## Async Formatting
Ensure workflows encapsulate natively wrapping `asyncio` execution boundaries cleanly mirroring best practices logically maintaining deterministic event isolation safely without hanging logic traces randomly generating unexpected protocol timeouts!
- **Pure Returns**: Write sequential loops returning strict native models avoiding wrapping external libraries abstracting context bounds dangerously breaking the validation states functionally matching standard yield traces transparently.
- **Delegation Safety**: Always inject constraint mapping passing the core memory trace logs uniformly down spun child components ensuring execution traces stack visually perfectly maintaining transparency locally!
