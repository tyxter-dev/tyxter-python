from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateTemplateRequest,
    DuplicateTemplateRequest,
    EstimateTemplateCostRequest,
    ListTemplatesResponse,
    TemplateAnalyticsResponse,
    TemplateCostEstimateResponse,
    TemplateGenerationRequest,
    TemplateGenerationResponse,
    TemplateResponse,
    UpdateTemplateRequest,
)

from ._base import Resource, path_id


class TemplatesResource(Resource):
    def create(self, payload: CreateTemplateRequest) -> TemplateResponse:
        return cast(TemplateResponse, self._request("POST", "/v1/templates", json=payload))

    def generate(
        self,
        payload: TemplateGenerationRequest,
        *,
        idempotency_key: str | None = None,
    ) -> TemplateGenerationResponse:
        return cast(
            TemplateGenerationResponse,
            self._request(
                "POST",
                "/v1/templates/generate",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListTemplatesResponse:
        return cast(
            ListTemplatesResponse,
            self._request(
                "GET",
                "/v1/templates",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def retrieve(self, template_id: str) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request("GET", f"/v1/templates/{path_id('template_id', template_id)}"),
        )

    def update(self, template_id: str, payload: UpdateTemplateRequest) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request(
                "PATCH",
                f"/v1/templates/{path_id('template_id', template_id)}",
                json=payload,
            ),
        )

    def submit(self, template_id: str) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request("POST", f"/v1/templates/{path_id('template_id', template_id)}/submit"),
        )

    def duplicate(
        self,
        template_id: str,
        payload: DuplicateTemplateRequest | None = None,
    ) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request(
                "POST",
                f"/v1/templates/{path_id('template_id', template_id)}/duplicate",
                json=payload or {},
            ),
        )

    def analytics(self, template_id: str) -> TemplateAnalyticsResponse:
        return cast(
            TemplateAnalyticsResponse,
            self._request("GET", f"/v1/templates/{path_id('template_id', template_id)}/analytics"),
        )

    def estimate_cost(
        self,
        template_id: str,
        payload: EstimateTemplateCostRequest | None = None,
    ) -> TemplateCostEstimateResponse:
        return cast(
            TemplateCostEstimateResponse,
            self._request(
                "POST",
                f"/v1/templates/{path_id('template_id', template_id)}/estimate-cost",
                json=payload or {},
            ),
        )

    def delete(self, template_id: str) -> TemplateResponse:
        return cast(
            TemplateResponse,
            self._request("DELETE", f"/v1/templates/{path_id('template_id', template_id)}"),
        )
