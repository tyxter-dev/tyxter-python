from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .common import Environment

MetaSignupSessionStatus: TypeAlias = Literal["pending", "processing", "completed", "expired"]


class CreateMetaSignupSessionRequest(TypedDict):
    return_url: str
    end_customer_ref: NotRequired[str]


class MetaSignupSessionResponse(TypedDict):
    id: str
    object: Literal["meta_signup_session"]
    status: MetaSignupSessionStatus
    url: str | None
    return_url: str
    end_customer_ref: str | None
    project_id: str
    environment_id: str
    environment: Environment
    expires_at: str
    completed_at: str | None
    provider_connection_id: str | None
    created_at: str
    updated_at: str
