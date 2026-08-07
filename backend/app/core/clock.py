"""Injectable clock, ID, and scheduler context boundaries."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Protocol
from uuid import uuid4


class Clock(Protocol):
    def now(self) -> datetime:
        ...


@dataclass(frozen=True, slots=True)
class FixedClock:
    fixed_time: datetime

    def now(self) -> datetime:
        return self.fixed_time


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(datetime.now().astimezone().tzinfo)


class IdGenerator(Protocol):
    def generate(self, prefix: str = "") -> str:
        ...


class DeterministicIdGenerator:
    __slots__ = ("prefix", "counter")

    def __init__(self, prefix: str = "", counter: int = 0) -> None:
        self.prefix = prefix
        self.counter = counter

    def generate(self, prefix: str = "") -> str:
        self.counter += 1
        return f"{prefix}{self.prefix}{self.counter:08d}"


class SystemIdGenerator:
    def generate(self, prefix: str = "") -> str:
        return f"{prefix}{uuid4().hex}"


_current_clock: ContextVar[Clock] = ContextVar("current_clock")
_current_id_generator: ContextVar[IdGenerator] = ContextVar("current_id_generator")


def get_clock() -> Clock:
    try:
        return _current_clock.get()
    except LookupError:
        return SystemClock()


def get_id_generator() -> IdGenerator:
    try:
        return _current_id_generator.get()
    except LookupError:
        return SystemIdGenerator()


@contextmanager
def bind_clock(clock: Clock) -> Iterator[None]:
    token = _current_clock.set(clock)
    try:
        yield
    finally:
        _current_clock.reset(token)


@contextmanager
def bind_id_generator(generator: IdGenerator) -> Iterator[None]:
    token = _current_id_generator.set(generator)
    try:
        yield
    finally:
        _current_id_generator.reset(token)


@dataclass(frozen=True, slots=True)
class SchedulerContext:
    scheduled_time: datetime
    actual_start_time: datetime | None = None
    attempt: int = 0
    is_retry: bool = False
    is_delayed: bool = False
    delay_reason: str | None = None


_scheduler_context: ContextVar[SchedulerContext | None] = ContextVar(
    "scheduler_context", default=None
)


def get_scheduler_context() -> SchedulerContext | None:
    return _scheduler_context.get(None)


@contextmanager
def bind_scheduler_context(context: SchedulerContext) -> Iterator[None]:
    token = _scheduler_context.set(context)
    try:
        yield
    finally:
        _scheduler_context.reset(token)


def generate_run_id() -> str:
    return get_id_generator().generate("run-")


def generate_attempt_id() -> str:
    return get_id_generator().generate("attempt-")
