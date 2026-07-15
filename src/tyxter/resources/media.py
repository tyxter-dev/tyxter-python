from __future__ import annotations

from typing import cast

from tyxter.errors import TyxterMediaUploadError
from tyxter.types import (
    CreateMediaUploadRequest,
    DeleteMediaAssetResponse,
    ListMediaAssetsResponse,
    MediaAssetResponse,
    MediaKind,
    MediaLifecycle,
    MediaStatus,
    MediaStorageUsageResponse,
    MediaUploadResponse,
    UploadMediaInput,
)

from ._base import Resource, path_id


class MediaResource(Resource):
    def create_upload(
        self,
        payload: CreateMediaUploadRequest,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MediaUploadResponse:
        return cast(
            MediaUploadResponse,
            self._request(
                "POST",
                "/v1/media/uploads",
                json=payload,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def complete_upload(
        self,
        asset_id: str,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MediaAssetResponse:
        return cast(
            MediaAssetResponse,
            self._request(
                "POST",
                f"/v1/media/uploads/{path_id('asset_id', asset_id)}/complete",
                idempotency_key=idempotency_key,
                trace_id=trace_id,
            ),
        )

    def retrieve(self, asset_id: str, *, trace_id: str | None = None) -> MediaAssetResponse:
        return cast(
            MediaAssetResponse,
            self._request(
                "GET",
                f"/v1/media/{path_id('asset_id', asset_id)}",
                trace_id=trace_id,
            ),
        )

    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        lifecycle: MediaLifecycle | None = None,
        status: MediaStatus | None = None,
        kind: MediaKind | None = None,
        trace_id: str | None = None,
    ) -> ListMediaAssetsResponse:
        return cast(
            ListMediaAssetsResponse,
            self._request(
                "GET",
                "/v1/media",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "lifecycle": lifecycle,
                    "status": status,
                    "kind": kind,
                },
                trace_id=trace_id,
            ),
        )

    def delete(self, asset_id: str, *, trace_id: str | None = None) -> DeleteMediaAssetResponse:
        return cast(
            DeleteMediaAssetResponse,
            self._request(
                "DELETE",
                f"/v1/media/{path_id('asset_id', asset_id)}",
                trace_id=trace_id,
            ),
        )

    def storage_usage(self, *, trace_id: str | None = None) -> MediaStorageUsageResponse:
        return cast(
            MediaStorageUsageResponse,
            self._request("GET", "/v1/media/storage-usage", trace_id=trace_id),
        )

    def upload(
        self,
        input: UploadMediaInput,
        *,
        create_idempotency_key: str | None = None,
        complete_idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MediaAssetResponse:
        request: CreateMediaUploadRequest = {
            "kind": input["kind"],
            "mime_type": input["mime_type"],
            "byte_length": input["byte_length"],
        }
        if "lifecycle" in input:
            request["lifecycle"] = input["lifecycle"]
        if "filename" in input:
            request["filename"] = input["filename"]

        session = self.create_upload(
            request,
            idempotency_key=create_idempotency_key,
            trace_id=trace_id,
        )
        upload_response = self._client._request_absolute(
            session["upload_method"],
            session["upload_url"],
            content=input["body"],
            headers=session["upload_headers"],
        )
        if upload_response.is_error:
            raise TyxterMediaUploadError(upload_response.status_code)
        return self.complete_upload(
            session["id"],
            idempotency_key=complete_idempotency_key,
            trace_id=trace_id,
        )
