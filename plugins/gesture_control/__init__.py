"""Gesture Control Plugin for Hermes Agent."""

import json
import subprocess
import sys
from pathlib import Path

def register(ctx):
    """Registers the gesture control plugin tools."""

    def start_gesture_control(task_id: str = None) -> str:
        """Launches the MediaPipe gesture control camera tracking script."""
        script_path = Path(__file__).parent / "gesture_tracker.py"
        try:
            subprocess.Popen([sys.executable, str(script_path)])
            return json.dumps({
                "status": "success",
                "message": "MediaPipe hand gesture control active. Use index finger to move mouse cursor and pinch to click."
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to start gesture tracker: {str(e)}"
            })

    ctx.register_tool(
        name="start_gesture_control",
        toolset="gesture",
        schema={
            "name": "start_gesture_control",
            "description": "Starts camera-based hand gesture tracking to control the computer mouse and click.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=lambda args, **kw: start_gesture_control(kw.get("task_id")),
    )
