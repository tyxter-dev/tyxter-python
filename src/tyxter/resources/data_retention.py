from __future__ import annotations

from typing import cast

from tyxter.types import DataRetentionPolicyResponse, UpdateDataRetentionPolicyRequest

from ._base import Resource


class DataRetentionResource(Resource):
    def retrieve(self) -> DataRetentionPolicyResponse:
        return cast(
            DataRetentionPolicyResponse,
            self._request("GET", "/v1/data-retention"),
        )

    def update(
        self,
        payload: UpdateDataRetentionPolicyRequest,
        *,
        idempotency_key: str | None = None,
    ) -> DataRetentionPolicyResponse:
        return cast(
            DataRetentionPolicyResponse,
            self._request(
                "PATCH",
                "/v1/data-retention",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )
