from __future__ import annotations

from typing import Literal, cast

from tyxter.types import ListRateCardsResponse, RateCardResponse

from ._base import Resource


class RateCardsResource(Resource):
    def list(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        currency: Literal["brl"] | None = None,
    ) -> ListRateCardsResponse:
        return cast(
            ListRateCardsResponse,
            self._request(
                "GET",
                "/v1/rate-cards",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "currency": currency,
                },
            ),
        )

    def retrieve_current(self) -> RateCardResponse:
        return cast(RateCardResponse, self._request("GET", "/v1/rate-cards/current"))
