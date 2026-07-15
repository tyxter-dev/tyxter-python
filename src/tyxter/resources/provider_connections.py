from __future__ import annotations

from typing import cast

from tyxter.types import (
    CreateProviderCredentialSetupSessionRequest,
    DeleteProviderConnectionResponse,
    ExchangeMetaOAuthCodeRequest,
    ListProviderConnectionsResponse,
    MetaOnboardingConfigResponse,
    ProviderConnectionResponse,
    ProviderConnectionStatusResponse,
    ProviderCredentialSetupSessionResponse,
    RegisterMetaConnectionRequest,
    RotateProviderConnectionTokenRequest,
)

from ._base import Resource, path_id


class ProviderCredentialSetupSessionsResource(Resource):
    def create(
        self,
        payload: CreateProviderCredentialSetupSessionRequest,
        *,
        idempotency_key: str | None = None,
    ) -> ProviderCredentialSetupSessionResponse:
        return cast(
            ProviderCredentialSetupSessionResponse,
            self._request(
                "POST",
                "/v1/provider-credential-setup-sessions",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def retrieve(self, request_id: str) -> ProviderCredentialSetupSessionResponse:
        return cast(
            ProviderCredentialSetupSessionResponse,
            self._request(
                "GET",
                f"/v1/provider-credential-setup-sessions/{path_id('request_id', request_id)}",
            ),
        )


class ProviderConnectionsResource(Resource):
    def list(
        self, *, limit: int | None = None, starting_after: str | None = None
    ) -> ListProviderConnectionsResponse:
        return cast(
            ListProviderConnectionsResponse,
            self._request(
                "GET",
                "/v1/provider-connections",
                params={"limit": limit, "starting_after": starting_after},
            ),
        )

    def status(self) -> ProviderConnectionStatusResponse:
        return cast(
            ProviderConnectionStatusResponse,
            self._request("GET", "/v1/provider-connections/status"),
        )

    def meta_onboarding(self) -> MetaOnboardingConfigResponse:
        return cast(
            MetaOnboardingConfigResponse,
            self._request("GET", "/v1/provider-connections/meta/onboarding"),
        )

    def register_meta(self, payload: RegisterMetaConnectionRequest) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request("POST", "/v1/provider-connections/meta", json=payload),
        )

    def exchange_meta_oauth(
        self, payload: ExchangeMetaOAuthCodeRequest
    ) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request("POST", "/v1/provider-connections/meta/oauth", json=payload),
        )

    def retrieve(self, connection_id: str) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request(
                "GET",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}",
            ),
        )

    def rotate_token(
        self,
        connection_id: str,
        payload: RotateProviderConnectionTokenRequest,
    ) -> ProviderConnectionResponse:
        return cast(
            ProviderConnectionResponse,
            self._request(
                "POST",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}/rotate",
                json=payload,
            ),
        )

    def delete(self, connection_id: str) -> DeleteProviderConnectionResponse:
        return cast(
            DeleteProviderConnectionResponse,
            self._request(
                "DELETE",
                f"/v1/provider-connections/{path_id('connection_id', connection_id)}",
            ),
        )
