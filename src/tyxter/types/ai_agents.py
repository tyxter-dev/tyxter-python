from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

AIAgentProvider: TypeAlias = Literal["anthropic", "openai"]
AIAgentMemoryPersistence: TypeAlias = Literal["disabled", "opt_in", "opt_out"]


class AIAgentBlockedTopicRule(TypedDict):
    match_type: Literal["keyword", "regex"]
    pattern: str
    label: NotRequired[str]


class CreateAIAgentRequest(TypedDict):
    name: str
    provider: AIAgentProvider
    model: str
    api_key: str
    system_prompt: str
    description: NotRequired[str]
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    daily_cost_cap_brl: NotRequired[str]
    handoff_phrases: NotRequired[list[str]]
    blocked_topics: NotRequired[list[AIAgentBlockedTopicRule]]
    blocked_topic_fallback_response: NotRequired[str]
    max_context_messages: NotRequired[int]
    max_context_age_seconds: NotRequired[int | None]
    memory_persistence: NotRequired[AIAgentMemoryPersistence]
    enabled: NotRequired[bool]


class UpdateAIAgentRequest(TypedDict, total=False):
    name: str
    description: str | None
    model: str
    api_key: str
    system_prompt: str
    max_tokens: int
    temperature: float
    daily_cost_cap_brl: str | None
    handoff_phrases: list[str]
    blocked_topics: list[AIAgentBlockedTopicRule]
    blocked_topic_fallback_response: str
    max_context_messages: int
    max_context_age_seconds: int | None
    memory_persistence: AIAgentMemoryPersistence
    enabled: bool
    archived: bool


class AIAgentResponse(TypedDict):
    id: str
    object: Literal["ai_agent"]
    name: str
    description: str | None
    provider: AIAgentProvider
    model: str
    environment: Environment
    system_prompt: str
    current_prompt_version: int
    max_tokens: int
    temperature: str
    daily_cost_cap_brl: str | None
    handoff_phrases: list[str]
    blocked_topics: list[AIAgentBlockedTopicRule]
    blocked_topic_fallback_response: str
    max_context_messages: int
    max_context_age_seconds: int | None
    memory_persistence: AIAgentMemoryPersistence
    enabled: bool
    api_key_suffix: str
    archived_at: str | None
    created_at: str
    updated_at: str


class ListAIAgentsResponse(TypedDict):
    object: Literal["list"]
    data: list[AIAgentResponse]
    has_more: bool
    next_cursor: str | None


class AIAgentPromptVersionResponse(TypedDict):
    id: str
    object: Literal["ai_agent_prompt_version"]
    ai_agent_id: str
    version: int
    system_prompt: str
    previous_system_prompt: str | None
    editor_actor_type: Literal["api_key", "session", "system"]
    editor_actor_id: str
    trace_id: str | None
    created_at: str


class ListAIAgentPromptVersionsResponse(TypedDict):
    object: Literal["list"]
    data: list[AIAgentPromptVersionResponse]
    has_more: bool
    next_cursor: str | None


class AIAgentCompletionMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
    created_at: NotRequired[str]


class AIAgentCompletionRequest(TypedDict):
    messages: list[AIAgentCompletionMessage]
    contact_phone: NotRequired[str]
    trace_id: NotRequired[str]


class AIAgentCompletionResponse(TypedDict):
    object: Literal["ai_agent_completion"]
    ai_agent_id: str
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_brl: str
    handoff: bool
    trace_id: str


class AIAgentResponseLogResponse(TypedDict):
    id: str
    object: Literal["ai_agent_response_log"]
    ai_agent_id: str
    prompt_version: int
    provider: AIAgentProvider
    model: str
    temperature: str
    max_tokens: int
    tokens_in: int
    tokens_out: int
    cost_brl: str
    contact_phone: str | None
    input_messages: list[AIAgentCompletionMessage]
    output_message: str
    trace_id: str | None
    created_at: str


class ListAIAgentResponseLogsResponse(TypedDict):
    object: Literal["list"]
    data: list[AIAgentResponseLogResponse]
    has_more: bool
    next_cursor: str | None


class DeleteAIAgentResponse(TypedDict):
    id: str
    deleted: Literal[True]
