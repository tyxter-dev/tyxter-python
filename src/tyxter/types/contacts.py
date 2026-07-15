from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment, JSONObject

ContactStatus: TypeAlias = Literal["opted_in", "opted_out"]
ContactSource: TypeAlias = Literal["api", "inbound_keyword", "dashboard_override"]


class ContactTagRef(TypedDict):
    id: str
    name: str
    color: str | None


class OptInRequest(TypedDict):
    phone: str
    source: NotRequired[ContactSource]
    metadata: NotRequired[JSONObject]


class OptOutRequest(TypedDict):
    phone: str
    source: NotRequired[ContactSource]
    reason: NotRequired[str]


class BulkImportContactRow(TypedDict):
    phone: str
    metadata: NotRequired[JSONObject]


class BulkImportContactsRequest(TypedDict):
    rows: list[BulkImportContactRow]
    source: NotRequired[ContactSource]


class ContactResponse(TypedDict):
    id: str
    object: Literal["contact"]
    phone: str
    status: ContactStatus
    environment: Environment
    opt_in_source: str | None
    opt_in_at: str | None
    opt_out_source: str | None
    opt_out_at: str | None
    metadata: JSONObject | None
    tags: NotRequired[list[ContactTagRef]]
    created_at: str
    updated_at: str


class ListContactsResponse(TypedDict):
    object: Literal["list"]
    data: list[ContactResponse]
    has_more: bool
    next_cursor: str | None


class BulkImportContactsResponse(TypedDict):
    object: Literal["list"]
    data: list[ContactResponse]
    imported: int
    skipped: int


class ContactDataExportResponse(TypedDict):
    object: Literal["contact_data_export"]
    contact: ContactResponse
    messages: list[JSONObject]
    generated_at: str


class ContactErasureResponse(TypedDict):
    object: Literal["contact_erasure"]
    contact_id: str
    erased_at: str
    messages_redacted: int
