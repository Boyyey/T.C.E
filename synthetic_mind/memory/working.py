from __future__ import annotations

from typing import List
import math
import time

from ..types import Experience


class WorkingMemory:
    def __init__(self, capacity: int = 8) -> None:
        self.capacity = capacity
        self.buffer: List[Experience] = []

    def add(self, exp: Experience) -> None:
        # Insert with base saliency influenced by novelty (length, punctuation)
        novelty = min(1.0, 0.2 + len(exp.content) / 200.0)
        exp.saliency = max(0.05, min(1.0, 0.5 * novelty))
        self.buffer.append(exp)
        self._trim()

    def _trim(self) -> None:
        if len(self.buffer) <= self.capacity:
            return
        # Drop lowest effective score first
        self.buffer.sort(key=lambda e: self._effective_score(e))
        self.buffer = self.buffer[-self.capacity :]
        # Preserve temporal order after trim
        self.buffer.sort(key=lambda e: e.timestamp)

    def _effective_score(self, e: Experience) -> float:
        # Recency decay + saliency
        age_s = max(0.0, time.time() - e.timestamp)
        recency = math.exp(-age_s / 120.0)  # ~2 min half-life-ish
        return 0.6 * e.saliency + 0.4 * recency

    def topk(self, k: int) -> List[Experience]:
        return sorted(self.buffer, key=lambda e: self._effective_score(e), reverse=True)[:k]

    def reinforce(self, items: List[Experience], delta: float = 0.1) -> None:
        ids = {i.id for i in items}
        for e in self.buffer:
            if e.id in ids:
                e.saliency = min(1.0, e.saliency + delta)
            else:
                e.saliency = max(0.01, e.saliency * 0.98)
