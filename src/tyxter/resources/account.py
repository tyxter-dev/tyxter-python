from __future__ import annotations

from typing import cast

from tyxter.types import AccountProfileResponse

from ._base import Resource


class AccountResource(Resource):
    def retrieve(self) -> AccountProfileResponse:
        return cast(AccountProfileResponse, self._request("GET", "/v1/account"))

    def me(self) -> AccountProfileResponse:
        return cast(AccountProfileResponse, self._request("GET", "/v1/me"))
