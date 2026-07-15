from __future__ import annotations

import argparse
import csv
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tyxter import Tyxter
from tyxter.types import CreateMessageBatchRequest, MessageBatchResponse, VariableValue

PHONE_RE = re.compile(r"^\+\d{8,15}$")
MAX_BATCH_RECIPIENTS = 10_000


@dataclass(frozen=True)
class Customer:
    phone: str
    variables: Mapping[str, VariableValue]


def read_customer_list(path: Path) -> list[Customer]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("customer CSV must include a header row")
        if "phone" not in reader.fieldnames:
            raise ValueError("customer CSV must include a phone column")

        customers: list[Customer] = []
        for row_number, row in enumerate(reader, start=2):
            phone = (row.get("phone") or "").strip()
            if not PHONE_RE.fullmatch(phone):
                raise ValueError(f"row {row_number}: phone must be E.164, e.g. +5511999999999")

            variables = {
                key: value.strip()
                for key, value in row.items()
                if key != "phone" and value is not None and value.strip()
            }
            customers.append(Customer(phone=phone, variables=variables))

    if not customers:
        raise ValueError("customer CSV must include at least one customer")
    if len(customers) > MAX_BATCH_RECIPIENTS:
        raise ValueError(f"customer CSV cannot exceed {MAX_BATCH_RECIPIENTS} customers")
    return customers


def build_batch_payload(
    customers: list[Customer],
    *,
    from_phone_number_id: str,
    template_name: str,
    template_language: str,
    batch_name: str | None = None,
) -> CreateMessageBatchRequest:
    if not from_phone_number_id:
        raise ValueError("from_phone_number_id is required")
    if not template_name:
        raise ValueError("template_name is required")
    if not template_language:
        raise ValueError("template_language is required")

    payload: CreateMessageBatchRequest = {
        "channel": "whatsapp",
        "from": from_phone_number_id,
        "template": {"name": template_name, "language": template_language},
        "recipients": [
            {"to": customer.phone, "variables": dict(customer.variables)}
            if customer.variables
            else {"to": customer.phone}
            for customer in customers
        ],
    }
    if batch_name:
        payload["name"] = batch_name
    return payload


def send_broadcast(
    client: Tyxter,
    *,
    customers: list[Customer],
    from_phone_number_id: str,
    template_name: str,
    template_language: str,
    batch_name: str | None = None,
    idempotency_key: str | None = None,
) -> MessageBatchResponse:
    payload = build_batch_payload(
        customers,
        from_phone_number_id=from_phone_number_id,
        template_name=template_name,
        template_language=template_language,
        batch_name=batch_name,
    )
    return client.batches.create(payload, idempotency_key=idempotency_key)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send a Tyxter template broadcast to a CSV customer list.",
    )
    parser.add_argument(
        "--customers",
        required=True,
        type=Path,
        help="CSV file with a phone column",
    )
    parser.add_argument(
        "--from",
        dest="from_phone_number_id",
        required=True,
        help="Tyxter phone ID",
    )
    parser.add_argument("--template-name", required=True, help="Approved template name")
    parser.add_argument("--template-language", default="en_US", help="Template language code")
    parser.add_argument("--name", dest="batch_name", help="Optional batch display name")
    parser.add_argument("--idempotency-key", help="Stable retry key for this broadcast")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("TYXTER_API_KEY"),
        help="Tyxter API key",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("TYXTER_API_BASE_URL", "https://api.tyxter.com"),
        help="Tyxter API base URL",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    if not args.api_key:
        parser.error("--api-key or TYXTER_API_KEY is required")

    customers = read_customer_list(args.customers)
    client = Tyxter(api_key=args.api_key, base_url=args.base_url)
    batch = send_broadcast(
        client,
        customers=customers,
        from_phone_number_id=args.from_phone_number_id,
        template_name=args.template_name,
        template_language=args.template_language,
        batch_name=args.batch_name,
        idempotency_key=args.idempotency_key,
    )

    print(f"created batch {batch['id']} for {len(customers)} customers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
