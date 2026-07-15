from __future__ import annotations

from typing import cast

from tyxter.types import (
    ConnectPhoneNumberRequest,
    ListAvailableRegionsResponse,
    ListPhoneNumbersResponse,
    PhoneNumberResponse,
    PhoneNumberStatus,
    ProvisionPhoneNumberRequest,
    TransferPhoneNumberRequest,
)

from ._base import Resource, path_id


class PhoneNumbersResource(Resource):
    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        status: PhoneNumberStatus | None = None,
    ) -> ListPhoneNumbersResponse:
        return cast(
            ListPhoneNumbersResponse,
            self._request(
                "GET",
                "/v1/phone-numbers",
                params={"limit": limit, "starting_after": starting_after, "status": status},
            ),
        )

    def retrieve(self, phone_number_id: str) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "GET", f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}"
            ),
        )

    def provision(
        self,
        payload: ProvisionPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/provision",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def connect(
        self,
        payload: ConnectPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                "/v1/phone-numbers/connect",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def disconnect(self, phone_number_id: str) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "DELETE", f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}"
            ),
        )

    def release(
        self, phone_number_id: str, *, idempotency_key: str | None = None
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/release",
                idempotency_key=idempotency_key,
            ),
        )

    def transfer(
        self,
        phone_number_id: str,
        payload: TransferPhoneNumberRequest,
        *,
        idempotency_key: str | None = None,
    ) -> PhoneNumberResponse:
        return cast(
            PhoneNumberResponse,
            self._request(
                "POST",
                f"/v1/phone-numbers/{path_id('phone_number_id', phone_number_id)}/transfer",
                json=payload,
                idempotency_key=idempotency_key,
            ),
        )

    def list_available_regions(self) -> ListAvailableRegionsResponse:
        return cast(
            ListAvailableRegionsResponse,
            self._request("GET", "/v1/phone-numbers/available-regions"),
        )
