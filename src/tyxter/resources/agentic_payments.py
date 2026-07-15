from __future__ import annotations

from typing import cast

from tyxter.types import (
    AgenticAuthorizationResponse,
    AgenticAuthorizationStatus,
    AgenticPaymentResponse,
    AgenticPaymentStatus,
    CreateAgenticAuthorizationRequest,
    CreateAgenticPaymentRequest,
    ListAgenticAuthorizationsResponse,
    ListAgenticBanksResponse,
    ListAgenticPaymentsResponse,
)

from ._base import Resource, path_id


class AgenticPaymentsResource(Resource):
    def list_banks(
        self, *, search: str | None = None, limit: int | None = None
    ) -> ListAgenticBanksResponse:
        return cast(
            ListAgenticBanksResponse,
            self._request("GET", "/v1/agentic/banks", params={"search": search, "limit": limit}),
        )

    def create_authorization(
        self,
        payload: CreateAgenticAuthorizationRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> AgenticAuthorizationResponse:
        return cast(
            AgenticAuthorizationResponse,
            self._request(
                "POST",
                "/v1/agentic/authorizations",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def list_authorizations(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: AgenticAuthorizationStatus | None = None,
        customer_tax_id: str | None = None,
    ) -> ListAgenticAuthorizationsResponse:
        return cast(
            ListAgenticAuthorizationsResponse,
            self._request(
                "GET",
                "/v1/agentic/authorizations",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "status": status,
                    "customer_tax_id": customer_tax_id,
                },
            ),
        )

    def retrieve_authorization(self, authorization_id: str) -> AgenticAuthorizationResponse:
        return cast(
            AgenticAuthorizationResponse,
            self._request(
                "GET",
                f"/v1/agentic/authorizations/{path_id('authorization_id', authorization_id)}",
            ),
        )

    def revoke_authorization(
        self,
        authorization_id: str,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> AgenticAuthorizationResponse:
        return cast(
            AgenticAuthorizationResponse,
            self._request(
                "POST",
                "/v1/agentic/authorizations/"
                f"{path_id('authorization_id', authorization_id)}/revoke",
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def create_payment(
        self,
        payload: CreateAgenticPaymentRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> AgenticPaymentResponse:
        return cast(
            AgenticPaymentResponse,
            self._request(
                "POST",
                "/v1/agentic/payments",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def list_payments(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: AgenticPaymentStatus | None = None,
        customer_tax_id: str | None = None,
    ) -> ListAgenticPaymentsResponse:
        return cast(
            ListAgenticPaymentsResponse,
            self._request(
                "GET",
                "/v1/agentic/payments",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "status": status,
                    "customer_tax_id": customer_tax_id,
                },
            ),
        )

    def retrieve_payment(self, payment_id: str) -> AgenticPaymentResponse:
        return cast(
            AgenticPaymentResponse,
            self._request("GET", f"/v1/agentic/payments/{path_id('payment_id', payment_id)}"),
        )

    def cancel_payment(
        self,
        payment_id: str,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> AgenticPaymentResponse:
        return cast(
            AgenticPaymentResponse,
            self._request(
                "POST",
                f"/v1/agentic/payments/{path_id('payment_id', payment_id)}/cancel",
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )
