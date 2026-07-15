from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import JSONObject, JSONValue

AutomationStatus: TypeAlias = Literal["draft", "active", "paused", "archived"]
AutomationTriggerKind: TypeAlias = Literal[
    "manual", "webhook", "inbound_message", "flow_completed", "schedule"
]
AutomationNodeType: TypeAlias = Literal[
    "manual.trigger",
    "webhook.trigger",
    "inbound_message.trigger",
    "flow_completed.trigger",
    "schedule.trigger",
    "ai_agent.invoke",
    "http.request",
    "condition",
    "delay",
    "time_gate",
    "message.send",
    "template.send",
    "webhook.emit",
]
AutomationRunStatus: TypeAlias = Literal[
    "queued", "running", "waiting", "completed", "failed", "cancelled", "timed_out"
]
AutomationStepRunStatus: TypeAlias = Literal[
    "queued", "running", "waiting", "skipped", "completed", "failed", "cancelled"
]


class AutomationNodePosition(TypedDict):
    x: float
    y: float


class AutomationGraphNode(TypedDict):
    id: str
    type: AutomationNodeType
    config: JSONObject
    label: NotRequired[str]
    position: NotRequired[AutomationNodePosition]


class AutomationGraphEdge(TypedDict):
    id: str
    source: str
    target: str
    source_handle: NotRequired[str]
    condition: NotRequired[str]


class AutomationGraph(TypedDict):
    version: Literal["automation_graph_v1"]
    nodes: list[AutomationGraphNode]
    edges: list[AutomationGraphEdge]


class AutomationValidationIssue(TypedDict):
    code: str
    message: str
    node_id: str | None
    path: list[str | int]


class CreateAutomationRequest(TypedDict):
    name: str
    description: NotRequired[str]


class UpdateAutomationRequest(TypedDict, total=False):
    name: str
    description: str | None
    status: AutomationStatus


class AutomationResponse(TypedDict):
    id: str
    object: Literal["automation"]
    name: str
    description: str | None
    status: AutomationStatus
    active_version_id: str | None
    trace_id: str | None
    archived_at: str | None
    created_at: str
    updated_at: str


class ListAutomationsResponse(TypedDict):
    object: Literal["list"]
    data: list[AutomationResponse]
    has_more: bool
    next_cursor: str | None


class DeleteAutomationResponse(TypedDict):
    id: str
    deleted: Literal[True]


class CreateAutomationVersionRequest(TypedDict):
    graph: AutomationGraph


class PublishAutomationRequest(TypedDict):
    version_id: str


class AutomationVersionResponse(TypedDict):
    id: str
    object: Literal["automation_version"]
    automation_id: str
    version: int
    graph: AutomationGraph
    graph_hash: str
    validation_errors: list[AutomationValidationIssue]
    published_at: str | None
    trace_id: str | None
    created_at: str


class ListAutomationVersionsResponse(TypedDict):
    object: Literal["list"]
    data: list[AutomationVersionResponse]
    has_more: bool
    next_cursor: str | None


class CreateAutomationRunRequest(TypedDict, total=False):
    input: JSONObject
    idempotency_key: str
    trace_id: str


class AutomationRunResponse(TypedDict):
    id: str
    object: Literal["automation_run"]
    automation_id: str
    automation_version_id: str
    trigger_id: str | None
    trigger_kind: AutomationTriggerKind
    status: AutomationRunStatus
    input_summary: JSONObject | None
    output_summary: JSONObject | None
    error_code: str | None
    error_message: str | None
    current_node_id: str | None
    started_at: str | None
    completed_at: str | None
    cancelled_at: str | None
    trace_id: str
    created_at: str
    updated_at: str


class ListAutomationRunsResponse(TypedDict):
    object: Literal["list"]
    data: list[AutomationRunResponse]
    has_more: bool
    next_cursor: str | None


class AutomationStepRunResponse(TypedDict):
    id: str
    object: Literal["automation_step_run"]
    automation_run_id: str
    node_id: str
    node_type: AutomationNodeType
    attempt: int
    status: AutomationStepRunStatus
    input_summary: JSONObject | None
    output_summary: JSONObject | None
    error_code: str | None
    error_message: str | None
    scheduled_for: str | None
    started_at: str | None
    completed_at: str | None
    trace_id: str
    created_at: str
    updated_at: str


class ListAutomationStepRunsResponse(TypedDict):
    object: Literal["list"]
    data: list[AutomationStepRunResponse]
    has_more: bool
    next_cursor: str | None


class AutomationWebhookSecretResponse(TypedDict):
    object: Literal["automation_webhook_secret"]
    automation_id: str
    automation_version_id: str
    trigger_id: str
    slug: str
    signing_secret: str


AutomationWebhookInput: TypeAlias = dict[str, JSONValue]
