from __future__ import annotations

from tyxter.message_builders import (
    instagram_media,
    instagram_text,
    whatsapp_audio_from_text,
    whatsapp_channel_media,
    whatsapp_channel_text,
    whatsapp_flow,
    whatsapp_interactive,
    whatsapp_media,
    whatsapp_template,
    whatsapp_text,
)
from tyxter.types import (
    InstagramMediaMessageInput,
    InstagramTextMessageInput,
    MessageResponse,
    WhatsAppChannelMediaMessageInput,
    WhatsAppChannelTextMessageInput,
    WhatsAppFlowMessageInput,
    WhatsAppInteractiveMessageInput,
    WhatsAppMediaMessageInput,
    WhatsAppTemplateMessageInput,
    WhatsAppTextMessageInput,
    WhatsAppTTSMessageInput,
)

from .messages import MessagesResource


class WhatsAppMessagesResource:
    def __init__(self, messages: MessagesResource) -> None:
        self._messages = messages

    def send_text(
        self,
        input: WhatsAppTextMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_text(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def send_media(
        self,
        input: WhatsAppMediaMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_media(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def send_audio_from_text(
        self,
        input: WhatsAppTTSMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_audio_from_text(input),
            idempotency_key=idempotency_key,
            trace_id=trace_id,
        )

    def send_template(
        self,
        input: WhatsAppTemplateMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_template(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def send_interactive(
        self,
        input: WhatsAppInteractiveMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_interactive(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def send_flow(
        self,
        input: WhatsAppFlowMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_flow(input), idempotency_key=idempotency_key, trace_id=trace_id
        )


class InstagramMessagesResource:
    def __init__(self, messages: MessagesResource) -> None:
        self._messages = messages

    def send_text(
        self,
        input: InstagramTextMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            instagram_text(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def send_media(
        self,
        input: InstagramMediaMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            instagram_media(input), idempotency_key=idempotency_key, trace_id=trace_id
        )


class WhatsAppChannelsResource:
    def __init__(self, messages: MessagesResource) -> None:
        self._messages = messages

    def publish_text(
        self,
        input: WhatsAppChannelTextMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_channel_text(input), idempotency_key=idempotency_key, trace_id=trace_id
        )

    def publish_media(
        self,
        input: WhatsAppChannelMediaMessageInput,
        *,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
    ) -> MessageResponse:
        return self._messages.create(
            whatsapp_channel_media(input), idempotency_key=idempotency_key, trace_id=trace_id
        )
