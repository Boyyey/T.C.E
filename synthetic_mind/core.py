from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .types import Experience, Thought, Action
from .memory.working import WorkingMemory
from .attention.controller import AttentionController
from .reasoning.engine import ReasoningEngine
from .action.effectors import ActionExecutor
from .self_model.model import SelfModel
from .goals.drives import GoalSystem
from .memory.long_term import LongTermMemory


class MindConfig(BaseModel):
    working_memory_capacity: int = 8
    storage_dir: Optional[str] = "storage"
    save_every_n_steps: int = 3


class SyntheticMind:
    def __init__(self, config: Optional[MindConfig] = None, trace: bool = False) -> None:
        self.config = config or MindConfig()
        self.trace_enabled = trace
        self.working_memory = WorkingMemory(capacity=self.config.working_memory_capacity)
        self.attention = AttentionController()
        self.reasoning = ReasoningEngine()
        self.action = ActionExecutor()
        self.self_model = SelfModel()
        self.goals = GoalSystem()
        self.long_term_memory = LongTermMemory(storage_dir=self.config.storage_dir)
        self.long_term_memory.load()
        self.last_trace: Dict[str, Any] = {}
        self._steps = 0

    def ingest(self, text: str) -> Experience:
        exp = Experience.from_text(text)
        self.working_memory.add(exp)
        return exp

    def _is_trivial(self, text: str) -> bool:
        t = text.strip().lower()
        if len(t) <= 24 and any(greet in t for greet in ["hi", "hello", "hey", "how are you", "what's up", "sup", "yo", "good morning", "good evening"]):
            return True
        return False

    def step(self, text: str) -> str:
        exp = self.ingest(text)
        self.self_model.note_state(current_intent="respond_to_prompt", observation=text)

        trivial = self._is_trivial(text)
        if trivial:
            spotlight: List[Experience] = self.attention.select(self.working_memory, self.goals)
        else:
            spotlight = self.attention.select_with_retrieval(self.working_memory, self.goals, self.long_term_memory, query=text)

        self.self_model.assess_contradictions([e.content for e in spotlight])
        thought: Thought = self.reasoning.think(spotlight, self.self_model, self.long_term_memory)
        composed = self.action.compose_full_answer(thought.proposal, thought.rationale, self.self_model.snapshot().get("uncertainty"))
        action: Action = Action(kind="say", payload= composed)
        output: str = self.action.execute(action)
        self.working_memory.reinforce(spotlight, delta=0.1)
        tags = self._extract_tags(text)
        self.long_term_memory.record_episode(query=text, response=output, thought=thought, tags=tags)
        self._steps += 1
        if not trivial and (self._steps % self.config.save_every_n_steps == 0):
            self.long_term_memory.save()
        if self.trace_enabled:
            self.last_trace = {
                "input": text,
                "spotlight": [e.summary() for e in spotlight],
                "thought": thought.model_dump(),
                "action": action.model_dump(),
                "self_model": self.self_model.snapshot(),
                "tags": tags,
                "trivial": trivial,
            }
        return output

    def why_did_you_say(self) -> str:
        if not self.last_trace:
            return "No prior action to explain."
        t = self.last_trace.get("thought", {})
        return f"Because: {t.get('rationale', 'no rationale')}"

    def what_dont_you_know(self) -> str:
        if not self.last_trace:
            return "I don't know yet; I need an input."
        u = self.self_model.snapshot().get("uncertainty", 0.2)
        if u > 0.6:
            return "I am uncertain about the premises and need clarification or evidence."
        if u > 0.3:
            return "I may be missing constraints; providing more details can help."
        return "I am confident about the last topic, but open to counterpoints."

    def summarize_chain_of_thought(self) -> str:
        if not self.last_trace:
            return "No chain available."
        t = self.last_trace.get("thought", {})
        spot = ", ".join(s.get("content", "")[:60] for s in self.last_trace.get("spotlight", [])[:3])
        return f"I focused on: {spot}. Rationale: {t.get('rationale', '')}. Plan: answer, verify, then ask a follow-up."

    def _extract_tags(self, text: str) -> List[str]:
        tags: List[str] = []
        lower = text.lower()
        for key in ["math", "reason", "self", "who", "what", "why", "how", "goal", "philosophy", "ethics", "science", "coding"]:
            if key in lower:
                tags.append(key)
        return tags
