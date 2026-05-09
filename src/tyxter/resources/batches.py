from __future__ import annotations

from typing import Any

from ._base import JSONDict, Resource, path_id


class BatchesResource(Resource):
    def create(
        self,
        payload: JSONDict,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/batches",
            json=payload,
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def get(self, batch_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/batches/{path_id('batch_id', batch_id)}")

    def retrieve(self, batch_id: str) -> dict[str, Any]:
        return self.get(batch_id)

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/v1/batches",
            params={"limit": limit, "starting_after": starting_after},
        )

    def pause(self, batch_id: str) -> dict[str, Any]:
        return self._request("POST", f"/v1/batches/{path_id('batch_id', batch_id)}/pause", json={})

    def resume(self, batch_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1/batches/{path_id('batch_id', batch_id)}/resume",
            json={},
        )

    def cancel(self, batch_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1/batches/{path_id('batch_id', batch_id)}/cancel",
            json={},
        )

    def failures(self, batch_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/batches/{path_id('batch_id', batch_id)}/failures")
