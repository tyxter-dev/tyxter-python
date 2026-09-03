from __future__ import annotations

from typing import cast
from uuid import uuid4

from tyxter.types import (
    CreateFeedbackRequest,
    FeedbackReceiptResponse,
    ListPublicFeedbackReportsResponse,
    PublicFeedbackReportResponse,
)

from ._base import Resource, path_id


class FeedbackResource(Resource):
    def list(
        self,
        *,
        after: str | None = None,
        limit: int | None = None,
    ) -> ListPublicFeedbackReportsResponse:
        return cast(
            ListPublicFeedbackReportsResponse,
            self._request("GET", "/v1/feedback", params={"after": after, "limit": limit}),
        )

    def get(self, feedback_report_id: str) -> PublicFeedbackReportResponse:
        return cast(
            PublicFeedbackReportResponse,
            self._request(
                "GET", f"/v1/feedback/{path_id('feedback_report_id', feedback_report_id)}"
            ),
        )

    def create(
        self,
        payload: CreateFeedbackRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> FeedbackReceiptResponse:
        if idempotency_key is None:
            idempotency_key = str(uuid4())
        elif not (idempotency_key := idempotency_key.strip()):
            raise ValueError("idempotency_key must be a non-blank string")
        return cast(
            FeedbackReceiptResponse,
            self._request(
                "POST",
                "/v1/feedback",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )
