"""Flushed case-level progress records for long disposable comparators."""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TextIO


class ProbeProgress:
    def __init__(self, path: Path):
        self.path = path
        self._output: TextIO | None = None
        self._started = 0.0
        self._completed_cases = 0

    def __enter__(self) -> "ProbeProgress":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._output = self.path.open("x", encoding="utf-8")
        self._started = time.monotonic()
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        assert self._output is not None
        self._output.close()
        self._output = None

    def _write(
        self, event: str, phase: str, case_index: int, replay_seed: int | None,
    ) -> None:
        if self._output is None:
            raise RuntimeError("ProbeProgress must be used as a context manager")
        record = {
            "event": event,
            "phase": phase,
            "case_index": case_index,
            "replay_seed": replay_seed,
            "elapsed_seconds": time.monotonic() - self._started,
            "completed_cases": self._completed_cases,
        }
        self._output.write(json.dumps(record, separators=(",", ":")) + "\n")
        self._output.flush()
        os.fsync(self._output.fileno())

    @contextmanager
    def case(
        self, phase: str, *, case_index: int, replay_seed: int | None = None,
    ) -> Iterator[None]:
        if not phase or case_index < 0:
            raise ValueError("phase must be non-empty and case_index must be non-negative")
        self._write("start", phase, case_index, replay_seed)
        yield
        self._completed_cases += 1
        self._write("complete", phase, case_index, replay_seed)
