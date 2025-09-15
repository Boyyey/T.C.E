from __future__ import annotations

from typing import Dict, Any


class GoalSystem:
    def __init__(self) -> None:
        self.goals: Dict[str, Any] = {
            "curiosity": 0.6,  # desire to gather info
            "coherence": 0.8,  # desire to keep responses consistent
        }

    def snapshot(self) -> Dict[str, Any]:
        return dict(self.goals)
