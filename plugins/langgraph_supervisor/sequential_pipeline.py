"""Sequential Agent Workflow Pipeline (Drafter -> Polisher)."""

from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from .utils import resolve_llm

# ── 1. Shared Pipeline State ──────────────────────────────────────────────────

class PipelineState(TypedDict):
    topic: str
    draft: str
    final_output: str


# ── 2. Pipeline Nodes ─────────────────────────────────────────────────────────

def draft_node(state: PipelineState) -> dict:
    """Node A: Generates comprehensive rough draft."""
    llm = resolve_llm(temperature=0.7)
    prompt = f"Write a comprehensive rough draft about: {state['topic']}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"draft": response.content}


def polish_node(state: PipelineState) -> dict:
    """Node B: Edits and polishes draft for professional publication."""
    llm = resolve_llm(temperature=0.3)
    prompt = (
        f"Edit and polish this draft for a professional audience.\n"
        f"Improve flow, clarity, structure, and executive presentation:\n\n"
        f"{state['draft']}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_output": response.content}


# ── 3. Build Linear Graph ─────────────────────────────────────────────────────

def build_sequential_graph():
    workflow = StateGraph(PipelineState)

    workflow.add_node("drafter", draft_node)
    workflow.add_node("polisher", polish_node)

    # Linear sequential edges
    workflow.add_edge(START, "drafter")
    workflow.add_edge("drafter", "polisher")
    workflow.add_edge("polisher", END)

    return workflow.compile()


def run_sequential_pipeline(topic: str) -> dict:
    """Executes the Sequential Pipeline workflow."""
    app = build_sequential_graph()
    initial_state: PipelineState = {
        "topic": topic,
        "draft": "",
        "final_output": "",
    }
    final_state = app.invoke(initial_state)
    return {
        "topic": topic,
        "draft": final_state.get("draft", ""),
        "final_output": final_state.get("final_output", ""),
    }
