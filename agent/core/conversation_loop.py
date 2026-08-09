"""
Conversation loop executor module for Hermes Agent.

Extracted low-level loop runner managing API call iterations, interrupt checks,
and tool call execution handling.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConversationLoopExecutor:
    """Orchestrates API calls and tool execution loops."""

    def __init__(
        self,
        max_iterations: int = 90,
        handle_tool_call_fn: Optional[Callable[[str, Dict[str, Any], Optional[str]], Any]] = None,
    ):
        self.max_iterations = max_iterations
        self.handle_tool_call_fn = handle_tool_call_fn

    def execute_turn(
        self,
        messages: List[Dict[str, Any]],
        call_model_fn: Callable[[List[Dict[str, Any]]], Any],
        task_id: Optional[str] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Run iterative LLM model calls and process returned tool calls."""
        iteration = 0
        while iteration < self.max_iterations:
            response = call_model_fn(messages)
            if not getattr(response, "tool_calls", None):
                content = getattr(response, "content", "") or ""
                messages.append({"role": "assistant", "content": content})
                return content, messages

            # Process tool calls
            tool_calls = response.tool_calls
            messages.append({"role": "assistant", "tool_calls": tool_calls})

            for tc in tool_calls:
                name = getattr(tc.function, "name", "") if hasattr(tc, "function") else tc.get("name")
                args = getattr(tc.function, "arguments", {}) if hasattr(tc, "function") else tc.get("arguments")
                result_str = ""
                if self.handle_tool_call_fn:
                    result_str = str(self.handle_tool_call_fn(name, args, task_id))
                messages.append({
                    "role": "tool",
                    "tool_call_id": getattr(tc, "id", "call_0"),
                    "content": result_str,
                })
            iteration += 1

        return "Max iterations reached.", messages
