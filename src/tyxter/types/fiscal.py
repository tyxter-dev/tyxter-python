from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import TypedDict

FiscalDocumentStatus: TypeAlias = Literal[
    "pending", "authorized", "rejected", "blocked", "canceled", "substituted"
]
FiscalSourceKind: TypeAlias = Literal["consumption_period", "subscription_term"]


class FiscalDocumentResponse(TypedDict):
    id: str
    object: Literal["fiscal_document"]
    organization_id: str
    status: FiscalDocumentStatus
    source_kind: FiscalSourceKind
    source_id: str
    serie: str
    numero: int
    chave_acesso: str | None
    amount_brl: str
    competence_date: str | None
    receipt_date: str | None
    cancellation_deadline_at: str | None
    rejection_cstat: str | None
    rejection_reason: str | None
    danfse_available: bool
    xml_available: bool
    created_at: str
    updated_at: str


class ListFiscalDocumentsResponse(TypedDict):
    object: Literal["list"]
    data: list[FiscalDocumentResponse]
    has_more: bool
    next_cursor: str | None


class FiscalDocumentDownloadResponse(TypedDict):
    object: Literal["fiscal_document_download"]
    fiscal_document_id: str
    artifact: Literal["danfse", "xml"]
    url: str
    expires_at: str
