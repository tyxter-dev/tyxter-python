from __future__ import annotations

from typing import Any

from ._base import JSONDict, Resource, path_id


class ContactsResource(Resource):
    def opt_in(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/contacts/opt-in",
            json=payload,
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def opt_out(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/contacts/opt-out",
            json=payload,
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/v1/contacts",
            params={"limit": limit, "starting_after": starting_after},
        )

    def bulk_import(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/contacts/bulk-import",
            json=payload,
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def export(self, contact_id: str) -> dict[str, Any]:
        return self._request("POST", f"/v1/contacts/{path_id('contact_id', contact_id)}/export")

    def erase(self, contact_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/v1/contacts/{path_id('contact_id', contact_id)}")
