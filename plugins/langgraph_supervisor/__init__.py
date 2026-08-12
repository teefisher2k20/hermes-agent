"""LangGraph Supervisor & Sequential Workflows Plugin Entry Point."""

import json
from .supervisor import run_command_supervisor
from .data_jarvis_supervisor import run_data_jarvis_supervisor
from .sequential_pipeline import run_sequential_pipeline

def register(ctx):
    """Registers all LangGraph workflow tools."""

    # 1. Command Supervisor Tool
    ctx.register_tool(
        name="langgraph_supervisor",
        toolset="workflow",
        schema={
            "name": "langgraph_supervisor",
            "description": "Executes complex tasks using Command routing in LangGraph multi-agent supervisor (coder, researcher).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The complex task or workflow prompt to execute.",
                    }
                },
                "required": ["task"],
            },
        },
        handler=lambda args, **kw: json.dumps({"status": "success", "result": run_command_supervisor(args.get("task", ""))}),
    )

    # 2. Data Jarvis 3-Worker Supervisor Tool
    ctx.register_tool(
        name="data_jarvis_supervisor",
        toolset="workflow",
        schema={
            "name": "data_jarvis_supervisor",
            "description": "Orchestrates multi-agent execution across Researcher (facts), Analyst (insights), and Writer (final draft).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The research, analysis, and writing task prompt.",
                    }
                },
                "required": ["task"],
            },
        },
        handler=lambda args, **kw: json.dumps({"status": "success", "result": run_data_jarvis_supervisor(args.get("task", ""))}),
    )

    # 3. Sequential Pipeline Tool
    ctx.register_tool(
        name="sequential_pipeline",
        toolset="workflow",
        schema={
            "name": "sequential_pipeline",
            "description": "Executes a linear 2-stage drafting and polishing pipeline (Drafter -> Polisher).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic or subject to draft and polish.",
                    }
                },
                "required": ["topic"],
            },
        },
        handler=lambda args, **kw: json.dumps({"status": "success", "result": run_sequential_pipeline(args.get("topic", ""))}),
    )
