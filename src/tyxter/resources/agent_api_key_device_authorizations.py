from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

from tyxter.types import (
    AgentApiKeyDeviceAuthorizationResponse,
    AgentApiKeyDeviceTokenRequest,
    AgentApiKeyDeviceTokenResponse,
    CreateAgentApiKeyDeviceAuthorizationRequest,
)

if TYPE_CHECKING:
    from tyxter.client import TyxterBootstrap


class AgentApiKeyDeviceAuthorizationsResource:
    def __init__(self, client: TyxterBootstrap) -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Mapping[str, object],
        trace_id: str | None,
    ) -> object:
        return self._client._request(method, path, json=json, trace_id=trace_id)

    def create(
        self,
        payload: CreateAgentApiKeyDeviceAuthorizationRequest,
        *,
        trace_id: str | None = None,
    ) -> AgentApiKeyDeviceAuthorizationResponse:
        return cast(
            AgentApiKeyDeviceAuthorizationResponse,
            self._request(
                "POST",
                "/v1/agent-api-key-device-authorizations",
                json=payload,
                trace_id=trace_id,
            ),
        )

    def token(
        self,
        payload: AgentApiKeyDeviceTokenRequest,
        *,
        trace_id: str | None = None,
    ) -> AgentApiKeyDeviceTokenResponse:
        return cast(
            AgentApiKeyDeviceTokenResponse,
            self._request(
                "POST",
                "/v1/agent-api-key-device-authorizations/token",
                json=payload,
                trace_id=trace_id,
            ),
        )
