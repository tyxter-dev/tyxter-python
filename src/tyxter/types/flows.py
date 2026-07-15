from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import TypedDict

from .common import Environment, JSONObject

FlowStatus: TypeAlias = Literal["draft", "validated", "published", "archived"]


class CreateFlowRequest(TypedDict):
    name: str
    flow_json: JSONObject


class FlowResponse(TypedDict):
    id: str
    object: Literal["flow"]
    name: str
    status: FlowStatus
    environment: Environment
    flow_json: JSONObject
    provider_flow_id: str | None
    rejection_reason: str | None
    published_at: str | None
    created_at: str
    updated_at: str


class ListFlowsResponse(TypedDict):
    object: Literal["list"]
    data: list[FlowResponse]
    has_more: bool
    next_cursor: str | None
