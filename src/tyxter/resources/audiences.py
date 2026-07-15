from __future__ import annotations

from typing import cast

from tyxter.types import (
    AudienceResponse,
    CreateAudienceRequest,
    ListAudiencesResponse,
    UpdateAudienceRequest,
)

from ._base import Resource, path_id


class AudiencesResource(Resource):
    def create(self, payload: CreateAudienceRequest) -> AudienceResponse:
        return cast(AudienceResponse, self._request("POST", "/v1/audiences", json=payload))

    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListAudiencesResponse:
        return cast(
            ListAudiencesResponse,
            self._request(
                "GET",
                "/v1/audiences",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def retrieve(self, audience_id: str) -> AudienceResponse:
        return cast(
            AudienceResponse,
            self._request("GET", f"/v1/audiences/{path_id('audience_id', audience_id)}"),
        )

    def update(self, audience_id: str, payload: UpdateAudienceRequest) -> AudienceResponse:
        return cast(
            AudienceResponse,
            self._request(
                "PATCH",
                f"/v1/audiences/{path_id('audience_id', audience_id)}",
                json=payload,
            ),
        )

    def delete(self, audience_id: str) -> AudienceResponse:
        return cast(
            AudienceResponse,
            self._request("DELETE", f"/v1/audiences/{path_id('audience_id', audience_id)}"),
        )
