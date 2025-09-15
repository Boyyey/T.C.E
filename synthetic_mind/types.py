from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel, Field
import time


class Experience(BaseModel):
    id: str
    timestamp: float = Field(default_factory=lambda: time.time())
    modality: str = "text"
    content: str
    saliency: float = 0.5

    @staticmethod
    def from_text(text: str) -> "Experience":
        return Experience(id=f"exp-{int(time.time()*1000)}", content=text)

    def summary(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content, "saliency": round(self.saliency, 3)}


class Thought(BaseModel):
    mode: str  # "fast" | "slow" | "mixed"
    rationale: str
    proposal: str  # suggested response


class Action(BaseModel):
    kind: str = "say"
    payload: str
