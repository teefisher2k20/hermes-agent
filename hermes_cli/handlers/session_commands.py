"""
Session command handlers for Hermes CLI.

Extracted slash command handlers for /clear, /history, /resume, and /rename.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SessionCommandHandler:
    """Handles session state commands."""

    @staticmethod
    def handle_clear(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clear conversation transcript while preserving system prompt."""
        system_msgs = [m for m in messages if m.get("role") == "system"]
        logger.info("Session history cleared.")
        return system_msgs

    @staticmethod
    def handle_history_summary(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return structured summary of active conversation messages."""
        user_msgs = sum(1 for m in messages if m.get("role") == "user")
        assistant_msgs = sum(1 for m in messages if m.get("role") == "assistant")
        tool_msgs = sum(1 for m in messages if m.get("role") == "tool")
        return {
            "total_messages": len(messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "tool_messages": tool_msgs,
        }
