"""Shared LLM Resolver & Defensive Utilities for LangGraph Workflows."""

import logging
import os
from typing import Type, TypeVar, List, Dict, Any
from pydantic import BaseModel

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from hermes_cli.config import get_env_value

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

def resolve_llm(temperature: float = 0.0, default_model: str = None) -> ChatOpenAI:
    """Dynamically resolves LLM endpoint with fallback chain."""
    custom_model = default_model or os.getenv("SUPERVISOR_MODEL")
    if custom_model:
        base_url = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        return ChatOpenAI(
            model_name=custom_model,
            openai_api_base=base_url,
            openai_api_key=api_key,
            temperature=temperature,
            request_timeout=60,
        )

    openrouter_key = get_env_value("OPENROUTER_API_KEY")
    if openrouter_key:
        key = "sk-or-v1-" + openrouter_key[len("sk-or-v1-"):] if openrouter_key.lower().startswith("sk-or-v1-") else openrouter_key
        return ChatOpenAI(
            model_name="meta-llama/llama-3.3-70b-instruct",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=key,
            temperature=temperature,
            request_timeout=60,
        )

    return ChatOpenAI(
        model_name="qwen2.5-coder:7b",
        openai_api_base="http://127.0.0.1:11434/v1",
        openai_api_key="ollama",
        temperature=temperature,
        request_timeout=60,
    )


def safe_structured_invoke(llm: ChatOpenAI, schema: Type[T], messages: List[Any], fallback_instance: T) -> T:
    """Defensively invokes structured output LLM with exception fallback."""
    try:
        structured_llm = llm.with_structured_output(schema)
        return structured_llm.invoke(messages)
    except Exception as e:
        logger.warning(f"Structured LLM invocation failed ({str(e)}). Using fallback route.")
        return fallback_instance
