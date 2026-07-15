from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, TypedDict

from .messages import MediaKind

MediaLifecycle: TypeAlias = Literal["single_use", "library"]
MediaStatus: TypeAlias = Literal["pending", "ready", "consumed", "expired", "deleted"]


class CreateMediaUploadRequest(TypedDict):
    kind: MediaKind
    mime_type: str
    byte_length: int
    lifecycle: NotRequired[MediaLifecycle]
    filename: NotRequired[str]


class MediaUploadResponse(TypedDict):
    id: str
    object: Literal["media_upload"]
    upload_url: str
    upload_method: Literal["PUT"]
    upload_headers: dict[str, str]
    expires_at: str


class MediaAssetResponse(TypedDict):
    id: str
    object: Literal["media_asset"]
    kind: MediaKind
    lifecycle: MediaLifecycle
    filename: str | None
    mime_type: str
    byte_length: int
    status: MediaStatus
    expires_at: str | None
    upload_expires_at: str
    completed_at: str | None
    consumed_at: str | None
    consumed_by_message_id: str | None
    deleted_at: str | None
    trace_id: str | None
    created_at: str
    updated_at: str


class ListMediaAssetsResponse(TypedDict):
    object: Literal["list"]
    data: list[MediaAssetResponse]
    has_more: bool
    next_cursor: str | None


class DeleteMediaAssetResponse(TypedDict):
    id: str
    object: Literal["media_asset"]
    deleted: Literal[True]


class MediaStorageUsageResponse(TypedDict):
    object: Literal["media_storage_usage"]
    used_bytes: int
    limit_bytes: int
    available_bytes: int
    percent_used: float


class UploadMediaInput(CreateMediaUploadRequest):
    body: bytes
