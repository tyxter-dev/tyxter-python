from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict


class DataRetentionPolicyResponse(TypedDict):
    object: Literal["data_retention_policy"]
    retention_days: int
    data_export_enabled: bool
    updated_at: str | None


class UpdateDataRetentionPolicyRequest(TypedDict):
    retention_days: NotRequired[int]
    data_export_enabled: NotRequired[bool]
