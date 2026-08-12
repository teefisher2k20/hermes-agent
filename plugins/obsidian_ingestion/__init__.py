"""Obsidian Ingestion Plugin Entry Point."""

import json
from pathlib import Path
from .pipeline import run_obsidian_ingestion

def register(ctx):
    """Registers the Obsidian Ingestion Pipeline tool."""

    def handle_sync(vault_path: str = None, force: bool = False, task_id: str = None) -> str:
        """Triggers incremental Obsidian vault document hashing & Qdrant vector indexing."""
        try:
            path = Path(vault_path) if vault_path else Path(r"C:\Users\Terrance\Obsidian\Vault")
            result = run_obsidian_ingestion(vault_dir=path, force_reindex=force)
            return json.dumps(result)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Obsidian ingestion failed: {str(e)}"
            })

    ctx.register_tool(
        name="obsidian_ingestion",
        toolset="workflow",
        schema={
            "name": "obsidian_ingestion",
            "description": "Executes incremental document-hashed ingestion of Obsidian Markdown vault into local Qdrant vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vault_path": {
                        "type": "string",
                        "description": "Path to the Obsidian Vault directory.",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force full re-indexing regardless of document hash cache.",
                    }
                },
            },
        },
        handler=lambda args, **kw: handle_sync(args.get("vault_path"), args.get("force", False), kw.get("task_id")),
    )
