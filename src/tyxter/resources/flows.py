from __future__ import annotations

from typing import cast

from tyxter.types import CreateFlowRequest, FlowResponse, ListFlowsResponse

from ._base import Resource, path_id


class FlowsResource(Resource):
    def create(self, payload: CreateFlowRequest) -> FlowResponse:
        return cast(FlowResponse, self._request("POST", "/v1/flows", json=payload))

    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListFlowsResponse:
        return cast(
            ListFlowsResponse,
            self._request(
                "GET",
                "/v1/flows",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def retrieve(self, flow_id: str) -> FlowResponse:
        return cast(FlowResponse, self._request("GET", f"/v1/flows/{path_id('flow_id', flow_id)}"))

    def publish(self, flow_id: str, *, idempotency_key: str | None = None) -> FlowResponse:
        return cast(
            FlowResponse,
            self._request(
                "POST",
                f"/v1/flows/{path_id('flow_id', flow_id)}/publish",
                idempotency_key=idempotency_key,
            ),
        )
