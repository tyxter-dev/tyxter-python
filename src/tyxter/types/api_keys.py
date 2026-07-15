from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .account import APIKeyResponse
from .common import Environment

AgentApiKeyDeviceGrantType: TypeAlias = Literal["urn:ietf:params:oauth:grant-type:device_code"]


class CreateApiKeyRequest(TypedDict):
    name: str
    environment: Environment
    scopes: list[str]
    expires_at: NotRequired[str]


class RenameApiKeyRequest(TypedDict):
    name: str


class CreateApiKeyResponse(APIKeyResponse):
    secret: str


RotateApiKeyResponse: TypeAlias = CreateApiKeyResponse


class ListApiKeysResponse(TypedDict):
    object: Literal["list"]
    data: list[APIKeyResponse]
    has_more: bool
    next_cursor: str | None


class CreateAgentApiKeyDeviceAuthorizationRequest(TypedDict):
    client_name: str
    environment: Environment
    scopes: list[str]
    expires_at: NotRequired[str]


class AgentApiKeyDeviceAuthorizationResponse(TypedDict):
    object: Literal["agent_api_key_device_authorization"]
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class AgentApiKeyDeviceTokenRequest(TypedDict):
    grant_type: AgentApiKeyDeviceGrantType
    device_code: str


class AgentApiKeyPreflightCheck(TypedDict):
    id: Literal["account", "provider_status", "phone_numbers", "templates", "sandbox_quickstart"]
    method: Literal["GET"]
    path: str
    required_scopes: list[str]
    description: str


class AgentApiKeyPreflightResponse(TypedDict):
    object: Literal["agent_api_key_preflight"]
    checks: list[AgentApiKeyPreflightCheck]


class AgentApiKeyDeviceTokenPendingResponse(TypedDict):
    object: Literal["agent_api_key_device_token"]
    status: Literal["pending"]
    interval: int
    expires_in: int


class AgentApiKeyDeviceTokenApprovedResponse(TypedDict):
    object: Literal["agent_api_key_device_token"]
    status: Literal["approved"]
    api_key: CreateApiKeyResponse
    preflight: AgentApiKeyPreflightResponse


AgentApiKeyDeviceTokenResponse: TypeAlias = (
    AgentApiKeyDeviceTokenPendingResponse | AgentApiKeyDeviceTokenApprovedResponse
)
