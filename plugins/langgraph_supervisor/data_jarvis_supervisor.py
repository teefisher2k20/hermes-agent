"""Data Jarvis 3-Worker Multi-Agent Supervisor (Researcher -> Analyst -> Writer)."""

import logging
from typing import TypedDict, Literal
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from .utils import resolve_llm, safe_structured_invoke

logger = logging.getLogger(__name__)

# ── 1. Shared State Definition ────────────────────────────────────────────────

class AgentState(TypedDict):
    task: str
    messages: list
    next_agent: str


class RouteDecision(BaseModel):
    next_agent: Literal["researcher", "analyst", "writer", "FINISH"] = Field(
        description="The next worker agent to route to, or FINISH when task is complete."
    )
    reason: str = Field(description="Explanation for worker selection.")


# ── 2. Specialist Worker Nodes ───────────────────────────────────────────────

def research_node(state: AgentState) -> dict:
    """Researcher Specialist Node."""
    llm = resolve_llm(temperature=0.2)
    prompt = (
        f"You are the Researcher Agent. Task: {state['task']}\n"
        f"Gather factual information, web context, and background details.\n"
        f"Conversation history: {state['messages']}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": state["messages"] + [f"Researcher: {response.content}"]}


def analyst_node(state: AgentState) -> dict:
    """Analyst Specialist Node."""
    llm = resolve_llm(temperature=0.2)
    prompt = (
        f"You are the Analyst Agent. Task: {state['task']}\n"
        f"Analyze data, extract patterns, key insights, and actionable conclusions.\n"
        f"Conversation history: {state['messages']}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": state["messages"] + [f"Analyst: {response.content}"]}


def writer_node(state: AgentState) -> dict:
    """Writer Specialist Node."""
    llm = resolve_llm(temperature=0.3)
    prompt = (
        f"You are the Writer Agent. Task: {state['task']}\n"
        f"Synthesize research and analysis into a polished, executive final output.\n"
        f"Conversation history: {state['messages']}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": state["messages"] + [f"Writer: {response.content}"]}


# ── 3. Supervisor Node ────────────────────────────────────────────────────────

def supervisor_node(state: AgentState) -> dict:
    """Central Supervisor Hub Router."""
    llm = resolve_llm(temperature=0.0)

    system_prompt = (
        "You are a supervisor managing three specialists: 'researcher', 'analyst', and 'writer'.\n"
        f"Task: {state['task']}\n"
        "Decide who acts next based on progress:\n"
        "- Use 'researcher' to gather facts first.\n"
        "- Use 'analyst' to extract insights after research is collected.\n"
        "- Use 'writer' to produce the final polished output.\n"
        "- Output 'FINISH' when the final output is completely fulfilled."
    )

    fallback_decision = RouteDecision(
        next_agent="FINISH",
        reason="Fallback invoked due to upstream model parsing exception."
    )

    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=str(msg)) for msg in state["messages"]]
    decision = safe_structured_invoke(llm, RouteDecision, messages, fallback_decision)

    return {"next_agent": decision.next_agent}


# ── 4. Assemble Graph ─────────────────────────────────────────────────────────

def build_data_jarvis_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("supervisor", supervisor_node)

    # All workers report back to the supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", "supervisor")

    # Conditional edge routing
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "FINISH": END,
        },
    )

    workflow.add_edge(START, "supervisor")
    return workflow.compile()


def run_data_jarvis_supervisor(task: str) -> dict:
    """Executes the Data Jarvis Multi-Agent Supervisor workflow."""
    app = build_data_jarvis_graph()
    initial_state = {
        "task": task,
        "messages": [f"Initial Task: {task}"],
        "next_agent": "supervisor",
    }
    final_state = app.invoke(initial_state)
    return {
        "task": task,
        "next_agent": final_state.get("next_agent"),
        "steps_count": len(final_state.get("messages", [])),
        "messages": final_state.get("messages", []),
        "final_output": final_state["messages"][-1] if final_state.get("messages") else "Completed.",
    }
