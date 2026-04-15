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
    NEGOTIATING = auto()
    COMMITTED = auto()
    FLOWING = auto()
    SEALED = auto()
    DRIFTED = auto()


@dataclass(frozen=True)
class Bid:
    bid_id: UUID
    from_agent: str
    to_agent: str
    intent: dict[str, Any]
    constraints: dict[str, Any]


@dataclass(frozen=True)
class Echo:
    echo_id: UUID
    original_bid_id: UUID
    from_agent: str
    to_agent: str
    modified_intent: dict[str, Any]
    modified_constraints: dict[str, Any]
    message: str


@dataclass(frozen=True)
class Pact:
    pact_id: UUID
    bid: Bid
    initiator: str
    receiver: str
    depth: int = 0
    parent_pact_id: UUID | None = None


@dataclass(frozen=True)
class Flow:
    pact_id: UUID
    state: PactState = PactState.FLOWING
    trace: list[Any] = field(default_factory=list)


@dataclass(frozen=True)
class Spun:
    parent_pact_id: UUID
    child_pact: Pact


@dataclass(frozen=True)
class Yield:
    output: Any
    confidence: float
    trace: list[Any]
    cost: float
    spun_yields: list[Yield]
    signature: str = ""  # The cryptographic representation of honoring work natively


@dataclass(frozen=True)
class Seal:
    pact_id: UUID
    yield_data: Yield


@dataclass(frozen=True)
class Drift:
    reason: str
    trace: list[Any]
    depth: int
