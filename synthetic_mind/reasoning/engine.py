from __future__ import annotations

from typing import List
import re

from ..types import Thought, Experience
from ..self_model.model import SelfModel
from ..memory.long_term import LongTermMemory


class RuleEngine:
    def apply(self, context: str) -> str | None:
        text = context.lower()
        if any(q in text for q in ["who are you", "what are you", "what is your purpose"]):
            return "I am a synthetic mind prototype combining memory, attention, reasoning, and reflection."
        if "why did you" in text:
            return "I chose that response based on retrieved context and current intent to maintain coherence."
        if "don\'t know" in text or "not sure" in text:
            return "I acknowledge uncertainty and can ask clarifying questions or search memory."
        # Simple arithmetic: a op b (integers)
        m = re.search(r"(\d+)\s*([+\-*/x])\s*(\d+)", text)
        if m:
            a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
            if op in ['x', '*']:
                return f"{a}*{b} = {a*b}"
            if op == '+':
                return f"{a}+{b} = {a+b}"
            if op == '-':
                return f"{a}-{b} = {a-b}"
            if op == '/':
                if b == 0:
                    return "Division by zero is undefined."
                return f"{a}/{b} = {a/b}"
        return None


class ReasoningEngine:
    def __init__(self) -> None:
        self.rules = RuleEngine()

    def think(self, spotlight: List[Experience], self_model: SelfModel, ltm: LongTermMemory) -> Thought:
        context = " | ".join(e.content for e in spotlight[:6]) if spotlight else ""
        meta = self_model.snapshot()
        rule = self.rules.apply(context)
        if rule:
            proposal = rule
            mode = "slow"
            rationale = "Applied symbolic rule matching over context."
        else:
            mode = "mixed" if 0 < len(context) < 800 else "fast"
            retrieved = ltm.recent(2)
            tail = (" | ".join(r["response"] for r in retrieved)) if retrieved else ""
            proposal = self._propose_response(context=context, meta_label=meta.get("current_intent", ""), tail=tail)
            rationale = f"Used {mode} reasoning over spotlight ({len(spotlight)} items) with retrieval tail."
        return Thought(mode=mode, rationale=rationale, proposal=proposal)

    def _propose_response(self, context: str, meta_label: str, tail: str) -> str:
        base = "I am here. What would you like to explore?" if not context else f"I considered: {context}."
        if tail:
            base += f" I also recalled: {tail}."
        prefix = f"[{meta_label}] " if meta_label else ""
        return prefix + base + " My next step is to answer clearly and ask a clarifying question if uncertain."
