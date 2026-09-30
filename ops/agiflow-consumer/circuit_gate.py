"""Durable connector availability gate; control-core retains queue authority."""
from __future__ import annotations

import fcntl
import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Callable, Any


class GateError(RuntimeError):
    pass


class CircuitGate:
    def __init__(self, path: str | Path, *, clock: Callable[[], float] = time.time):
        self.path = Path(path)
        self.clock = clock
        self.fd: int | None = None

    def __enter__(self):
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.fd = os.open(str(self.path) + ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(self.fd)
            self.fd = None
            raise GateError("CONSUMER_ALREADY_RUNNING") from exc
        return self

    def __exit__(self, *args):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def _read(self) -> dict[str, Any]:
        if not self.path.exists() and not self.path.is_symlink():
            return {"version": 1, "state": "closed", "failure_count": 0, "retry_at": 0}
        try:
            fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "r") as f:
                obj = json.loads(f.read(8193))
            if not isinstance(obj, dict) or obj.get("version") != 1:
                raise ValueError()
            if obj.get("state") not in {"closed", "cooldown", "parked"}:
                raise ValueError()
            count, retry = obj["failure_count"], obj["retry_at"]
            if type(count) is not int or not 0 <= count <= 1000000:
                raise ValueError()
            if type(retry) not in (int, float) or not math.isfinite(retry) or retry < 0:
                raise ValueError()
            reason = obj.get("reason", "CONNECTOR_FAILURE")
            if not isinstance(reason, str) or len(reason) > 80 or not reason.replace("_", "").isalnum():
                raise ValueError()
            return obj
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise GateError("CIRCUIT_STATE_INVALID") from exc

    def _write(self, state: dict[str, Any]):
        fd, name = tempfile.mkstemp(prefix=self.path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(state, f, sort_keys=True, allow_nan=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(name, self.path)
            directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _failure(self, state, reason, retryable):
        count = min(state["failure_count"] + 1, 1000000)
        now = self.clock()
        if not math.isfinite(now) or now < 0:
            raise GateError("CLOCK_INVALID")
        retry_at = now + min(60 * 2 ** min(count - 1, 4), 900) if retryable else 0
        # Store fixed diagnostics only, never response bodies, tokens or payloads.
        reason = reason if isinstance(reason, str) and len(reason) <= 80 and reason.replace("_", "").isalnum() else "CONNECTOR_FAILURE"
        self._write({"version": 1, "state": "cooldown" if retryable else "parked",
                     "failure_count": count, "retry_at": retry_at, "reason": reason})
        return {"status": "COOLDOWN" if retryable else "PARKED",
                "claimed": None, "reason": reason, "retryable": retryable,
                "retry_at": retry_at, "failure_count": count,
                "owner_action_required": not retryable}

    def run(self, action, *, reset_probe=None):
        if self.fd is None:
            raise GateError("CIRCUIT_LOCK_REQUIRED")
        state = self._read()
        if reset_probe is not None:
            try:
                reset_probe()
            except Exception as exc:
                result = self._failure(state, getattr(exc, "code", type(exc).__name__),
                                       getattr(exc, "retryable", True))
                result["claimed"] = False
                return result
            self._write({"version": 1, "state": "closed", "failure_count": 0, "retry_at": 0})
            return {"status": "RESET", "claimed": False}
        if state["state"] == "parked":
            return {"status": "PARKED", "claimed": False, "reason": state.get("reason", "CONNECTOR_FAILURE"),
                    "owner_action_required": True}
        if state["state"] == "cooldown" and self.clock() < state["retry_at"]:
            return {"status": "COOLDOWN", "claimed": False, "retry_at": state["retry_at"]}
        try:
            result = action()
        except Exception as exc:
            return self._failure(state, getattr(exc, "code", type(exc).__name__),
                                 getattr(exc, "retryable", True))
        if result.get("status") == "RETRYABLE":
            outcome = self._failure(state, result.get("reason", "CONNECTOR_FAILURE"),
                                    result.get("retryable", True))
            outcome["claimed"] = bool(result.get("claimed"))
            return outcome
        self._write({"version": 1, "state": "closed", "failure_count": 0, "retry_at": 0})
        return result
