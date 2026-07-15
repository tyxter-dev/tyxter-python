from __future__ import annotations

from typing import cast

from tyxter.types import (
    Environment,
    ListUsageRecordsResponse,
    UsageGroupBy,
    UsageSummaryResponse,
)

from ._base import Resource


class UsageResource(Resource):
    def retrieve(
        self,
        *,
        period_start: str,
        period_end: str,
        environment: Environment | None = None,
        group_by: UsageGroupBy | None = None,
    ) -> UsageSummaryResponse:
        return cast(
            UsageSummaryResponse,
            self._request(
                "GET",
                "/v1/usage",
                params={
                    "period_start": period_start,
                    "period_end": period_end,
                    "environment": environment,
                    "group_by": group_by,
                },
            ),
        )

    def list_records(
        self,
        *,
        limit: int | None = None,
        starting_after: str | None = None,
        environment: Environment | None = None,
        meter_id: str | None = None,
        recorded_after: str | None = None,
        recorded_before: str | None = None,
    ) -> ListUsageRecordsResponse:
        return cast(
            ListUsageRecordsResponse,
            self._request(
                "GET",
                "/v1/usage/records",
                params={
                    "limit": limit,
                    "starting_after": starting_after,
                    "environment": environment,
                    "meter_id": meter_id,
                    "recorded_after": recorded_after,
                    "recorded_before": recorded_before,
                },
            ),
        )
