from __future__ import annotations

from typing import cast

from tyxter.types import CreateProjectRequest, ListProjectsResponse, ProjectResponse

from ._base import Resource, path_id


class ProjectsResource(Resource):
    def create(
        self,
        payload: CreateProjectRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ProjectResponse:
        return cast(
            ProjectResponse,
            self._request(
                "POST",
                "/v1/projects",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
    ) -> ListProjectsResponse:
        return cast(
            ListProjectsResponse,
            self._request(
                "GET",
                "/v1/projects",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def retrieve(self, project_id: str) -> ProjectResponse:
        return cast(
            ProjectResponse,
            self._request("GET", f"/v1/projects/{path_id('project_id', project_id)}"),
        )
