from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

LLMProvider: TypeAlias = Literal["anthropic", "openai"]
LLMMemoryPersistence: TypeAlias = Literal["disabled", "opt_in", "opt_out"]


class LLMBlockedTopicRule(TypedDict):
    match_type: Literal["keyword", "regex"]
    pattern: str
    label: NotRequired[str]


class UpsertLLMRouteRequest(TypedDict):
    provider: LLMProvider
    model: str
    api_key: str
    system_prompt: str
    phone_number_id: NotRequired[str]
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    daily_cost_cap_brl: NotRequired[str]
    handoff_phrases: NotRequired[list[str]]
    blocked_topics: NotRequired[list[LLMBlockedTopicRule]]
    blocked_topic_fallback_response: NotRequired[str]
    max_context_messages: NotRequired[int]
    max_context_age_seconds: NotRequired[int | None]
    memory_persistence: NotRequired[LLMMemoryPersistence]
    enabled: NotRequired[bool]


class UpdateLLMRouteRequest(TypedDict, total=False):
    model: str
    api_key: str
    system_prompt: str
    max_tokens: int
    temperature: float
    daily_cost_cap_brl: str | None
    handoff_phrases: list[str]
    blocked_topics: list[LLMBlockedTopicRule]
    blocked_topic_fallback_response: str
    max_context_messages: int
    max_context_age_seconds: int | None
    memory_persistence: LLMMemoryPersistence
    enabled: bool


class LLMRouteResponse(TypedDict):
    id: str
    object: Literal["llm_route"]
    phone_number_id: str | None
    provider: LLMProvider
    model: str
    environment: Environment
    system_prompt: str
    current_prompt_version: int
    max_tokens: int
    temperature: str
    daily_cost_cap_brl: str | None
    handoff_phrases: list[str]
    blocked_topics: list[LLMBlockedTopicRule]
    blocked_topic_fallback_response: str
    max_context_messages: int
    max_context_age_seconds: int | None
    memory_persistence: LLMMemoryPersistence
    enabled: bool
    api_key_suffix: str
    created_at: str
    updated_at: str


class DeleteLLMRouteResponse(TypedDict):
    id: str
    deleted: Literal[True]


class LLMRoutePromptVersionResponse(TypedDict):
    id: str
    object: Literal["llm_route_prompt_version"]
    llm_route_id: str
    version: int
    system_prompt: str
    previous_system_prompt: str | None
    editor_actor_type: Literal["api_key", "session", "system"]
    editor_actor_id: str
    trace_id: str | None
    created_at: str


class ListLLMRoutePromptVersionsResponse(TypedDict):
    object: Literal["list"]
    data: list[LLMRoutePromptVersionResponse]
    has_more: bool
    next_cursor: str | None


class LLMCompletionMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
    created_at: NotRequired[str]


class LLMCompletionRequest(TypedDict):
    messages: list[LLMCompletionMessage]
    contact_phone: NotRequired[str]
    phone_number_id: NotRequired[str]
    trace_id: NotRequired[str]


class LLMCompletionResponse(TypedDict):
    object: Literal["llm_completion"]
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_brl: str
    provider_cost_usd_estimate: str | None
    handoff: bool
    trace_id: str


class LLMResponseLogResponse(TypedDict):
    id: str
    object: Literal["llm_response_log"]
    llm_route_id: str
    prompt_version: int
    provider: LLMProvider
    model: str
    temperature: str
    max_tokens: int
    tokens_in: int
    tokens_out: int
    cost_brl: str
    contact_phone: str | None
    input_messages: list[LLMCompletionMessage]
    output_message: str
    trace_id: str | None
    created_at: str


class ListLLMResponseLogsResponse(TypedDict):
    object: Literal["list"]
    data: list[LLMResponseLogResponse]
    has_more: bool
    next_cursor: str | None
