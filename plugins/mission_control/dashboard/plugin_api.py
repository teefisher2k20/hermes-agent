"""
Mission Control Dashboard Plugin API.

Exposes endpoints for syncing agent fleet state, kanban tasks,
and active skin engine color tokens with the Mission Control UI.
"""

from fastapi import APIRouter
from hermes_cli.skin_engine import get_skin_css_dict, get_active_skin
from hermes_cli.kanban_db import read_board_metadata

router = APIRouter(prefix="/api/plugins/mission-control", tags=["mission-control"])


@router.get("/status")
def get_mission_control_status():
    """Return Mission Control synced agent fleet status and skin tokens."""
    skin = get_active_skin()
    theme_tokens = get_skin_css_dict()
    
    try:
        board = read_board_metadata()
    except Exception:
        board = {}
    
    return {
        "status": "active",
        "agent": {
            "name": skin.get_branding("agent_name", "Hermes Agent"),
            "welcome": skin.get_branding("welcome", ""),
            "prompt_symbol": skin.get_branding("prompt_symbol", "❯"),
        },
        "theme": theme_tokens,
        "kanban_summary": {
            "columns": len(board.get("columns", [])) if isinstance(board, dict) else 0,
            "tasks": len(board.get("tasks", [])) if isinstance(board, dict) else 0,
        }
    }


@router.get("/theme")
def get_mission_control_theme():
    """Return active skin engine color tokens formatted for CSS/Tailwind sync."""
    return get_skin_css_dict()
