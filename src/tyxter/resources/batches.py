from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateMessageBatchRequest,
    ListMessageBatchesResponse,
    MessageBatchFailureExportResponse,
    MessageBatchResponse,
)

from ._base import Resource, path_id


class BatchesResource(Resource):
    def create(
        self,
        payload: CreateMessageBatchRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageBatchResponse:
        return cast(
            MessageBatchResponse,
            self._request(
                "POST",
                "/v1/batches",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def get(self, batch_id: str, *, trace_id: str | None = None) -> MessageBatchResponse:
        return cast(
            MessageBatchResponse,
            self._request(
                "GET",
                f"/v1/batches/{path_id('batch_id', batch_id)}",
                trace_id=trace_id,
            ),
        )

    def retrieve(self, batch_id: str, *, trace_id: str | None = None) -> MessageBatchResponse:
        return self.get(batch_id, trace_id=trace_id)

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        trace_id: str | None = None,
    ) -> ListMessageBatchesResponse:
        return cast(
            ListMessageBatchesResponse,
            self._request(
                "GET",
                "/v1/batches",
                params={"limit": limit, "starting_after": starting_after},
                trace_id=trace_id,
            ),
        )

    def pause(self, batch_id: str, *, trace_id: str | None = None) -> MessageBatchResponse:
        return cast(
            MessageBatchResponse,
            self._request(
                "POST",
                f"/v1/batches/{path_id('batch_id', batch_id)}/pause",
                trace_id=trace_id,
            ),
        )

    def resume(self, batch_id: str, *, trace_id: str | None = None) -> MessageBatchResponse:
        return cast(
            MessageBatchResponse,
            self._request(
                "POST",
                f"/v1/batches/{path_id('batch_id', batch_id)}/resume",
                trace_id=trace_id,
            ),
        )

    def cancel(self, batch_id: str, *, trace_id: str | None = None) -> MessageBatchResponse:
        return cast(
            MessageBatchResponse,
            self._request(
                "POST",
                f"/v1/batches/{path_id('batch_id', batch_id)}/cancel",
                trace_id=trace_id,
            ),
        )

    def failures(
        self, batch_id: str, *, trace_id: str | None = None
    ) -> MessageBatchFailureExportResponse:
        return cast(
            MessageBatchFailureExportResponse,
            self._request(
                "GET",
                f"/v1/batches/{path_id('batch_id', batch_id)}/failures",
                trace_id=trace_id,
            ),
        )
