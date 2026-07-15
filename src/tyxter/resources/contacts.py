from __future__ import annotations

from typing import cast

from tyxter.types import (
    BulkImportContactsRequest,
    BulkImportContactsResponse,
    ContactDataExportResponse,
    ContactErasureResponse,
    ContactResponse,
    ContactStatus,
    ListContactsResponse,
    OptInRequest,
    OptOutRequest,
)

from ._base import Resource, path_id


class ContactsResource(Resource):
    def opt_in(
        self,
        payload: OptInRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ContactResponse:
        return cast(
            ContactResponse,
            self._request(
                "POST",
                "/v1/contacts/opt-in",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def opt_out(
        self,
        payload: OptOutRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ContactResponse:
        return cast(
            ContactResponse,
            self._request(
                "POST",
                "/v1/contacts/opt-out",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        search: str | None = None,
        status: ContactStatus | None = None,
        tag_id: str | None = None,
    ) -> ListContactsResponse:
        return cast(
            ListContactsResponse,
            self._request(
                "GET",
                "/v1/contacts",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "search": search,
                    "status": status,
                    "tag_id": tag_id,
                },
            ),
        )

    def bulk_import(
        self,
        payload: BulkImportContactsRequest,
        *,
        idempotency_key: str | None = None,
    ) -> BulkImportContactsResponse:
        return cast(
            BulkImportContactsResponse,
            self._request(
                "POST",
                "/v1/contacts/bulk-import",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def export(self, contact_id: str) -> ContactDataExportResponse:
        return cast(
            ContactDataExportResponse,
            self._request(
                "POST",
                f"/v1/contacts/{path_id('contact_id', contact_id)}/export",
            ),
        )

    def erase(self, contact_id: str) -> ContactErasureResponse:
        return cast(
            ContactErasureResponse,
            self._request("DELETE", f"/v1/contacts/{path_id('contact_id', contact_id)}"),
        )
