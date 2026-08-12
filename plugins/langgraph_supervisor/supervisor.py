"""LangGraph Multi-Agent Supervisor Pattern using Command Routing."""

import logging
from typing import Literal
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, END, StateGraph, START
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent

from .utils import resolve_llm, safe_structured_invoke

logger = logging.getLogger(__name__)

# ── 1. Structured Output Routing Schema & State ───────────────────────────────

class RouteDecision(BaseModel):
    next_agent: Literal["coder", "researcher", "FINISH"] = Field(
        description="The next specialized agent to route to, or FINISH if the task is completely fulfilled."
    )
    reason: str = Field(description="Reasoning behind agent selection.")
    task_description: str = Field(description="Instructions or task for the selected agent.")


class AgentState(MessagesState):
    next: str


# ── 2. Supervisor Node ────────────────────────────────────────────────────────

def supervisor_node(state: AgentState) -> Command[Literal["coder", "researcher", "__end__"]]:
    """Central Supervisor Node enforcing Pydantic structured output routing."""
    llm = resolve_llm(temperature=0.0)

    system_prompt = (
        "You are a supervisor managing a 'coder' and a 'researcher'.\n"
        "Review the conversation history and decide who acts next.\n"
        "If the overarching task is completely fulfilled, respond with FINISH."
    )
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]

    fallback_decision = RouteDecision(
        next_agent="FINISH",
        reason="Fallback invoked due to upstream model parsing exception.",
        task_description="Task finalized via defensive fallback."
    )

    decision = safe_structured_invoke(llm, RouteDecision, messages, fallback_decision)

    goto = decision.next_agent
    if goto == "FINISH":
        goto = END

    return Command(goto=goto, update={"next": str(goto)})


# ── 3. Sub-Agent Nodes ────────────────────────────────────────────────────────

def coder_node(state: AgentState) -> Command[Literal["supervisor"]]:
    """Coder Sub-Agent Node equipped with script writing tools."""
    llm = resolve_llm(temperature=0.2)
    coder_agent = create_react_agent(llm, tools=[])
    result = coder_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="coder")]},
        goto="supervisor",
    )


def researcher_node(state: AgentState) -> Command[Literal["supervisor"]]:
    """Researcher Sub-Agent Node equipped with retrieval tools."""
    llm = resolve_llm(temperature=0.2)
    researcher_agent = create_react_agent(llm, tools=[])
    result = researcher_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="researcher")]},
        goto="supervisor",
    )


# ── 4. Assemble & Compile StateGraph ──────────────────────────────────────────

def build_supervisor_app():
    """Assembles StateGraph using Command routing natively."""
    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("coder", coder_node)
    builder.add_node("researcher", researcher_node)

    builder.add_edge(START, "supervisor")
    # Sub-agents natively return to the supervisor via Command(goto="supervisor")

    return builder.compile()


def run_command_supervisor(task_prompt: str) -> dict:
    """Invokes the compiled Command supervisor app."""
    app = build_supervisor_app()
    initial_state = {"messages": [HumanMessage(content=task_prompt)], "next": "supervisor"}
    final_state = app.invoke(initial_state)
    return {
        "task": task_prompt,
        "next": final_state.get("next"),
        "messages_count": len(final_state.get("messages", [])),
        "final_output": final_state["messages"][-1].content if final_state.get("messages") else "Completed.",
    }
