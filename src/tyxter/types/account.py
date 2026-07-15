from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import TypedDict

from .common import Environment

APIKeyKind: TypeAlias = Literal["standard", "agent"]


class APIKeyResponse(TypedDict):
    id: str
    object: Literal["api_key"]
    name: str
    key_prefix: str
    scopes: list[str]
    kind: APIKeyKind
    status: Literal["active", "revoked"]
    environment: Environment
    last_used_at: str | None
    expires_at: str | None
    created_at: str
    revoked_at: str | None


class AccountOrganization(TypedDict):
    id: str
    object: Literal["organization"]
    name: str
    slug: str
    status: Literal["active", "suspended"]


class AccountProject(TypedDict):
    id: str
    object: Literal["project"]
    name: str
    slug: str


class AccountEnvironment(TypedDict):
    id: str
    object: Literal["environment"]
    kind: Environment
    name: str


class AccountOwner(TypedDict):
    id: str
    object: Literal["organization_member"]
    email: str
    name: str | None
    role: Literal["owner"]


class AccountProfileResponse(TypedDict):
    object: Literal["account_profile"]
    organization: AccountOrganization
    project: AccountProject
    environment: AccountEnvironment
    api_key: APIKeyResponse
    dashboard_owner: AccountOwner | None
