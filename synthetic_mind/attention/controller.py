from __future__ import annotations

from typing import List

from ..memory.working import WorkingMemory
from ..types import Experience
from ..goals.drives import GoalSystem
from ..memory.long_term import LongTermMemory


class AttentionController:
    def __init__(self) -> None:
        pass

    def select(self, wm: WorkingMemory, goals: GoalSystem, k: int = 4) -> List[Experience]:
        return wm.topk(k)

    def select_with_retrieval(self, wm: WorkingMemory, goals: GoalSystem, ltm: LongTermMemory, query: str, k: int = 6) -> List[Experience]:
        wm_items = wm.topk(max(2, k // 2))
        retrieved = ltm.search(query, top_k=max(2, k))
        exps: List[Experience] = list(wm_items)
        for idx, score in retrieved[: max(1, k - len(exps))]:
            ep = ltm.episodes[idx]
            content = f"LT:{score:.2f} Q:{ep['query']} A:{ep['response']}"
            exps.append(Experience(id=f"ltm-{idx}", content=content, saliency=min(1.0, 0.4 + score * 0.6)))
        return exps[:k]
