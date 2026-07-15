from __future__ import annotations

from typing_extensions import assert_type

from tyxter import Tyxter
from tyxter.types import (
    CreateMessageRequest,
    ListMessagesResponse,
    MessageDetailResponse,
    MessageResponse,
)


def core_usage(client: Tyxter) -> None:
    request: CreateMessageRequest = {
        "channel": "whatsapp",
        "sender": {"type": "whatsapp_phone_number", "id": "pn_123"},
        "recipient": {"type": "phone_e164", "id": "+15555550100"},
        "message": {"type": "text", "text": {"body": "hello"}},
    }

    assert_type(client.messages.create(request), MessageResponse)
    assert_type(client.messages.list(status="sent"), ListMessagesResponse)
    assert_type(client.messages.retrieve("msg_123"), MessageDetailResponse)
    assert_type(client.messages.cancel("msg_123"), MessageDetailResponse)
