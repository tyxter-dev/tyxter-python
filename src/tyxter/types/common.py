from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

Environment: TypeAlias = Literal["sandbox", "production"]
JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]
QueryValue: TypeAlias = str | int | float | bool


class CursorPage(TypedDict):
    object: Literal["list"]
    has_more: bool
    next_cursor: str | None


class DeleteResponse(TypedDict):
    id: str
    deleted: bool


class TraceOptions(TypedDict):
    idempotency_key: NotRequired[str]
    trace_id: NotRequired[str]
