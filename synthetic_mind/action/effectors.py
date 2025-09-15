from __future__ import annotations

import ast
import builtins
from typing import Optional
import requests

from ..types import Action, Thought
from ..goals.drives import GoalSystem


SAFE_BUILTINS = {
    k: getattr(builtins, k)
    for k in ["abs", "min", "max", "sum", "len", "range", "enumerate", "sorted", "map", "filter", "any", "all"]
}


class ActionExecutor:
    def __init__(self) -> None:
        self.tools_enabled = True

    def decide(self, thought: Thought) -> Action:
        return Action(kind="say", payload=thought.proposal)

    def execute(self, action: Action) -> str:
        if action.kind == "say":
            return action.payload
        if action.kind == "web_search":
            return self._web_search(action.payload)
        if action.kind == "code_exec":
            return self._safe_exec(action.payload)
        return f"[unhandled action: {action.kind}]"

    def _web_search(self, query: str) -> str:
        try:
            r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=8)
            text = r.text
            # very naive extract of first result snippet
            start = text.find("result__snippet")
            if start != -1:
                snippet = text[start : start + 300]
                return f"Search snippet: {snippet}"
            return "No snippet extracted."
        except Exception as e:
            return f"Search error: {e}"

    def _safe_exec(self, code: str) -> str:
        try:
            ast.parse(code)  # syntax check
            env: dict = {"__builtins__": SAFE_BUILTINS}
            exec(code, env, env)
            result = env.get("result")
            return f"Code result: {result}"
        except Exception as e:
            return f"Exec error: {e}"

    def compose_full_answer(self, base: str, rationale: str, uncertainty: Optional[float] = None) -> str:
        parts = [base]
        parts.append(f"Reasoning: {rationale}")
        if uncertainty is not None:
            if uncertainty > 0.6:
                parts.append("I am uncertain; I propose to gather more context.")
            elif uncertainty > 0.3:
                parts.append("I am moderately confident; I welcome correction.")
            else:
                parts.append("I am confident in this answer.")
        parts.append("Would you like to go deeper or explore related questions?")
        return " \n".join(parts)
