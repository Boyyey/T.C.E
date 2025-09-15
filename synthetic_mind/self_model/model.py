from __future__ import annotations

from typing import Any, Dict, List
import time


class SelfModel:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = {
            "created_at": time.time(),
            "current_intent": None,
            "last_observation": None,
            "uncertainty": 0.2,
            "contradictions": [],
        }

    def note_state(self, current_intent: str, observation: str) -> None:
        self.state["current_intent"] = current_intent
        self.state["last_observation"] = observation
        self.state["updated_at"] = time.time()
        self._update_uncertainty(observation)

    def assess_contradictions(self, texts: List[str]) -> None:
        # Toy heuristic: flag if both strong affirmations and negations appear
        affirm = any(" is " in t.lower() and " not " not in t.lower() for t in texts)
        neg = any(" not " in t.lower() for t in texts)
        if affirm and neg:
            self.state.setdefault("contradictions", []).append({
                "ts": time.time(),
                "note": "Potential contradiction between affirmation and negation",
            })
            self.state["uncertainty"] = min(1.0, self.state.get("uncertainty", 0.2) + 0.1)

    def _update_uncertainty(self, observation: str) -> None:
        # Increase uncertainty when observation is vague; decrease when specific
        text = observation.strip()
        vague = len(text) < 8 or text.endswith("?")
        if vague:
            self.state["uncertainty"] = min(1.0, self.state.get("uncertainty", 0.2) + 0.05)
        else:
            self.state["uncertainty"] = max(0.05, self.state.get("uncertainty", 0.2) - 0.03)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self.state)
