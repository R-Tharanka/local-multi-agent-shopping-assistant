from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StateManager:
    _state: dict = field(default_factory=dict)

    def set(self, key: str, value) -> None:
        self._state[key] = value

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def snapshot(self) -> dict:
        return dict(self._state)

