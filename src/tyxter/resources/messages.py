from __future__ import annotations

from typing import Any

from ._base import JSONDict, Resource, path_id


class MessagesResource(Resource):
    def create(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/messages",
            json=payload,
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_text(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self.create(
            {**payload, "type": "text"},
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_template(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self.create(
            {**payload, "type": "template"},
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_media(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self.create(
            {**payload, "type": "media"},
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_interactive(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self.create(
            {**payload, "type": "interactive"},
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_flow(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self.create(
            {**payload, "type": "flow"},
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def get(self, message_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/messages/{path_id('message_id', message_id)}")

    def retrieve(self, message_id: str) -> dict[str, Any]:
        return self.get(message_id)

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: str | None = None,
        batch_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/v1/messages",
            params={
                "limit": limit,
                "starting_after": starting_after,
                "status": status,
                "batch_id": batch_id,
            },
        )
