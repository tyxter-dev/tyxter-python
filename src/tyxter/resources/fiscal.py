from __future__ import annotations

from typing import cast

from tyxter.types import (
    FiscalDocumentDownloadResponse,
    FiscalDocumentResponse,
    FiscalDocumentStatus,
    FiscalSourceKind,
    ListFiscalDocumentsResponse,
)

from ._base import Resource, path_id


class FiscalResource(Resource):
    def list_nfse(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: FiscalDocumentStatus | None = None,
        source_kind: FiscalSourceKind | None = None,
    ) -> ListFiscalDocumentsResponse:
        return cast(
            ListFiscalDocumentsResponse,
            self._request(
                "GET",
                "/v1/fiscal/nfse",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "status": status,
                    "source_kind": source_kind,
                },
            ),
        )

    def get_nfse(self, fiscal_document_id: str) -> FiscalDocumentResponse:
        return cast(
            FiscalDocumentResponse,
            self._request(
                "GET", f"/v1/fiscal/nfse/{path_id('fiscal_document_id', fiscal_document_id)}"
            ),
        )

    def download_danfse(self, fiscal_document_id: str) -> FiscalDocumentDownloadResponse:
        return cast(
            FiscalDocumentDownloadResponse,
            self._request(
                "GET",
                f"/v1/fiscal/nfse/{path_id('fiscal_document_id', fiscal_document_id)}/danfse",
            ),
        )

    def download_xml(self, fiscal_document_id: str) -> FiscalDocumentDownloadResponse:
        return cast(
            FiscalDocumentDownloadResponse,
            self._request(
                "GET",
                f"/v1/fiscal/nfse/{path_id('fiscal_document_id', fiscal_document_id)}/xml",
            ),
        )
