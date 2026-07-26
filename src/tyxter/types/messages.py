from __future__ import annotations

from typing import Literal, TypeAlias

from typing_extensions import NotRequired, Required, TypedDict

from .common import Environment, JSONObject, JSONValue

MessageChannel: TypeAlias = Literal["whatsapp", "instagram", "whatsapp_channel"]
MessageDirection: TypeAlias = Literal["inbound", "outbound"]
MessageIdentityType: TypeAlias = Literal[
    "whatsapp_phone_number",
    "phone_e164",
    "instagram_account",
    "instagram_user",
    "whatsapp_channel",
    "whatsapp_channel_audience",
]
MessageKind: TypeAlias = Literal["text", "template", "media", "interactive", "flow"]
MediaKind: TypeAlias = Literal["image", "document", "audio", "video", "sticker"]
VariableValue: TypeAlias = str | int | bool


class MessageIdentity(TypedDict):
    type: MessageIdentityType
    id: str


class TextMessagePayload(TypedDict):
    body: str
    preview_url: NotRequired[bool]


class TemplateHeaderMedia(TypedDict):
    kind: Literal["image", "document", "video"]
    asset_id: str


class TemplateMessagePayload(TypedDict):
    name: str
    language: str
    variables: NotRequired[dict[str, VariableValue]]
    components: NotRequired[list[JSONObject]]
    header_media: NotRequired[TemplateHeaderMedia]


class TTSMediaSource(TypedDict):
    type: Literal["tts"]
    provider: Literal["openai", "elevenlabs", "xai"]
    text: str
    voice: str
    language: str
    model: NotRequired[str]
    instructions: NotRequired[str]


class InlineMediaPayload(TypedDict):
    filename: str
    mime_type: str
    base64: str


class MediaMessagePayload(TypedDict):
    kind: MediaKind
    id: NotRequired[str]
    link: NotRequired[str]
    asset_id: NotRequired[str]
    inline: NotRequired[InlineMediaPayload]
    source: NotRequired[TTSMediaSource]
    caption: NotRequired[str]
    filename: NotRequired[str]
    mime_type: NotRequired[str]


class InteractiveMessagePayload(TypedDict):
    type: Literal["button", "list"]
    body: JSONObject
    action: JSONObject
    header: NotRequired[JSONObject]
    footer: NotRequired[JSONObject]


class FlowMessagePayload(TypedDict):
    type: Literal["flow"]
    body: JSONObject
    action: JSONObject
    header: NotRequired[JSONObject]
    footer: NotRequired[JSONObject]


class OutboundMessage(TypedDict):
    type: MessageKind
    text: NotRequired[TextMessagePayload]
    template: NotRequired[TemplateMessagePayload]
    media: NotRequired[MediaMessagePayload]
    interactive: NotRequired[InteractiveMessagePayload]
    flow: NotRequired[FlowMessagePayload]


class CreateMessageRequest(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    message: OutboundMessage
    metadata: NotRequired[JSONObject]


class SendTextMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    text: TextMessagePayload
    metadata: NotRequired[JSONObject]


class SendTemplateMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    template: TemplateMessagePayload
    metadata: NotRequired[JSONObject]


class SendMediaMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    media: MediaMessagePayload
    metadata: NotRequired[JSONObject]


class SendInteractiveMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    interactive: InteractiveMessagePayload
    metadata: NotRequired[JSONObject]


class SendFlowMessageInput(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageIdentity
    flow: FlowMessagePayload
    metadata: NotRequired[JSONObject]


class MessageResponse(TypedDict):
    id: str
    object: Literal["message"]
    status: str
    channel: MessageChannel
    environment: Environment
    template_id: str | None
    template_version_id: str | None
    template_version: int | None
    created_at: str
    trace_id: str


class MessageEventResponse(TypedDict):
    id: str
    type: str
    status: str | None
    payload: JSONValue | None
    created_at: str


class MessageProviderError(TypedDict):
    message: str | None
    type: str | None
    code: int | str | None
    error_subcode: int | str | None
    error_data: JSONValue | None
    fbtrace_id: str | None
    error_user_title: str | None
    error_user_msg: str | None


class MessageSummaryResponse(TypedDict):
    id: str
    object: Literal["message"]
    channel: MessageChannel
    direction: MessageDirection
    type: str
    status: str
    environment: Environment
    sender: MessageIdentity
    recipient: MessageIdentity
    provider: str | None
    provider_message_id: str | None
    template_name: str | None
    template_id: str | None
    template_version_id: str | None
    template_version: int | None
    payload: JSONValue | None
    metadata: JSONValue | None
    error_code: str | None
    error_message: str | None
    provider_error: MessageProviderError | None
    trace_id: str
    created_at: str
    updated_at: str


class MessageDetailResponse(MessageSummaryResponse):
    events: list[MessageEventResponse]


class ListMessagesResponse(TypedDict):
    object: Literal["list"]
    data: list[MessageSummaryResponse]
    has_more: bool
    next_cursor: str | None


WhatsAppTextMessageInput = TypedDict(
    "WhatsAppTextMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "body": Required[str],
        "preview_url": NotRequired[bool],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppMediaMessageInput = TypedDict(
    "WhatsAppMediaMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "media": Required[MediaMessagePayload],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTTSMessageInput = TypedDict(
    "WhatsAppTTSMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "tts": Required[TTSMediaSource],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTemplateMessageInput = TypedDict(
    "WhatsAppTemplateMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "name": Required[str],
        "language": Required[str],
        "variables": NotRequired[dict[str, VariableValue]],
        "components": NotRequired[list[JSONObject]],
        "header_media": NotRequired[TemplateHeaderMedia],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppInteractiveMessageInput = TypedDict(
    "WhatsAppInteractiveMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "interactive": Required[InteractiveMessagePayload],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppFlowMessageInput = TypedDict(
    "WhatsAppFlowMessageInput",
    {
        "from": Required[str],
        "to": Required[str],
        "flow": Required[FlowMessagePayload],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)


class InstagramTextMessageInput(TypedDict):
    account_id: str
    user_id: str
    body: str
    preview_url: NotRequired[bool]
    metadata: NotRequired[JSONObject]


class InstagramMediaMessageInput(TypedDict):
    account_id: str
    user_id: str
    media: MediaMessagePayload
    metadata: NotRequired[JSONObject]


class WhatsAppChannelTextMessageInput(TypedDict):
    channel_id: str
    body: str
    preview_url: NotRequired[bool]
    metadata: NotRequired[JSONObject]


class WhatsAppChannelMediaMessageInput(TypedDict):
    channel_id: str
    media: MediaMessagePayload
    metadata: NotRequired[JSONObject]
