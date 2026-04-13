"""
AIP Primitives.

We built agents on top of APIs, but APIs were built for a different world. 
Agents don't exchange resources. Agents do work.
AIP connects minds through commitment, coordination, and the nature of work itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
from uuid import UUID


class PactState(Enum):
    """
    The states a piece of agent work passes through.
    """
    NEGOTIATING = auto()
    COMMITTED = auto()
    FLOWING = auto()
    SEALED = auto()
    DRIFTED = auto()


@dataclass(frozen=True)
class Bid:
    """
    The initiating gesture. One agent reaches toward another with intent.
    Not a request, but the opening of a negotiation.
    """
    bid_id: UUID
    from_agent: str
    to_agent: str
    intent: dict[str, Any]
    constraints: dict[str, Any]  # Expected keys: budget, deadline, depth_limit, echo_limit


@dataclass(frozen=True)
class Echo:
    """
    A Bid returning reshaped. Negotiation in motion. 
    Intent preserved, terms changed. Agents say 'not like that, but like this' before committing.
    """
    echo_id: UUID
    original_bid_id: UUID
    from_agent: str
    to_agent: str
    modified_intent: dict[str, Any]
    modified_constraints: dict[str, Any]
    message: str


@dataclass(frozen=True)
class Pact:
    """
    The atom of AIP. A mutual commitment formed when Bid and Echo converge.
    Every Pact binds exactly two parties: an initiator and a receiver.
    Work requires negotiation, commitment, and trust.
    """
    pact_id: UUID
    bid: Bid
    initiator: str
    receiver: str
    depth: int = 0
    parent_pact_id: UUID | None = None


@dataclass(frozen=True)
class Flow:
    """
    The active state of a Pact in motion. 
    Work takes time. It is not an instantaneous API call; it flows.
    """
    pact_id: UUID
    state: PactState = PactState.FLOWING
    trace: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class Spun:
    """
    A child Pact born inside a parent Pact. Delegation is native.
    When a task is too large, work fractures into smaller units.
    """
    parent_pact_id: UUID
    child_pact: Pact


@dataclass(frozen=True)
class Yield:
    """
    The verified output of a Sealed Pact. 
    It carries proof that the work was real, a trace of its journey, and its cost.
    """
    output: Any
    confidence: float  # Scale of 0.0 to 1.0
    trace: list[Any]
    cost: float
    spun_yields: list[Yield]


@dataclass(frozen=True)
class Seal:
    """
    A Pact that honored its commitment. 
    The work converges, the pact closes cleanly, and it produces a Yield.
    """
    pact_id: UUID
    yield_data: Yield


@dataclass(frozen=True)
class Drift:
    """
    A Pact that could not hold. 
    Work involves uncertainty; work can fail. When it does, it drifts rather than crashing, 
    leaving the traces of where things unraveled.
    """
    reason: str
    trace: list[Any]
    depth: int
