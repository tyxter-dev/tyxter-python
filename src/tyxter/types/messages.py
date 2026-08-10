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


class StructuredPhoneRecipient(TypedDict):
    type: Literal["phone_e164"]
    country_calling_code: str
    national_number: str


class StructuredPhoneInput(TypedDict):
    country_calling_code: str
    national_number: str


MessageRecipient: TypeAlias = MessageIdentity | StructuredPhoneRecipient


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


class OrderDetailsAmount(TypedDict):
    value: int
    offset: Literal[100]


class OrderDetailsTax(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]


class OrderDetailsExpiration(TypedDict):
    timestamp: str
    description: str


class OrderDetailsItem(TypedDict):
    retailer_id: str
    name: str
    amount: OrderDetailsAmount
    quantity: int
    sale_amount: NotRequired[OrderDetailsAmount]


class OrderDetailsShipping(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]


class OrderDetailsDiscount(TypedDict):
    value: int
    offset: Literal[100]
    description: NotRequired[str]
    discount_program_name: NotRequired[str]


class NativePixOrder(TypedDict):
    status: Literal["pending"]
    tax: OrderDetailsTax
    items: list[OrderDetailsItem]
    subtotal: OrderDetailsAmount
    catalog_id: NotRequired[str]
    expiration: NotRequired[OrderDetailsExpiration]
    shipping: NotRequired[OrderDetailsShipping]
    discount: NotRequired[OrderDetailsDiscount]


class NativePixDynamicCode(TypedDict):
    code: str
    merchant_name: str
    key: str
    key_type: Literal["CPF", "CNPJ", "EMAIL", "PHONE", "EVP"]


class NativePixPaymentSetting(TypedDict):
    type: Literal["pix_dynamic_code"]
    pix_dynamic_code: NativePixDynamicCode


class NativePixText(TypedDict):
    text: str


class NativePixImageHeader(TypedDict):
    type: Literal["image"]
    link: str


class NativePixOrderDetailsParameters(TypedDict):
    reference_id: str
    type: Literal["digital-goods", "physical-goods"]
    payment_type: Literal["br"]
    payment_settings: tuple[NativePixPaymentSetting]
    currency: Literal["BRL"]
    total_amount: OrderDetailsAmount
    order: NotRequired[NativePixOrder]


class NativePixOrderDetailsAction(TypedDict):
    name: Literal["review_and_pay"]
    parameters: NativePixOrderDetailsParameters


class NativePixOrderDetailsMessagePayload(TypedDict):
    type: Literal["order_details"]
    body: NativePixText
    action: NativePixOrderDetailsAction
    header: NotRequired[NativePixImageHeader]
    footer: NotRequired[NativePixText]


InteractivePayload: TypeAlias = InteractiveMessagePayload | NativePixOrderDetailsMessagePayload


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
    interactive: NotRequired[InteractivePayload]
    flow: NotRequired[FlowMessagePayload]


class CreateMessageRequest(TypedDict):
    channel: MessageChannel
    sender: MessageIdentity
    recipient: MessageRecipient
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
    interactive: InteractivePayload
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
    status_reason: str | None
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


class InboundMessageMediaFailure(TypedDict):
    code: str
    message: str


class _InboundMessageMediaBase(TypedDict):
    asset_id: str
    kind: MediaKind
    mime_type: str
    byte_length: int
    filename: str | None
    provider_media_id: NotRequired[str]


class InboundMessageMediaConsumed(_InboundMessageMediaBase):
    status: Literal["consumed"]


class InboundMessageMediaFailed(_InboundMessageMediaBase):
    status: Literal["failed"]
    failure: InboundMessageMediaFailure


class InboundMessageMediaExpired(_InboundMessageMediaBase):
    status: Literal["expired"]


class InboundMessageMediaDeleted(_InboundMessageMediaBase):
    status: Literal["deleted"]


InboundMessageMediaDescriptor: TypeAlias = (
    InboundMessageMediaConsumed
    | InboundMessageMediaFailed
    | InboundMessageMediaExpired
    | InboundMessageMediaDeleted
)


class MessageSummaryResponse(TypedDict):
    id: str
    object: Literal["message"]
    channel: MessageChannel
    direction: MessageDirection
    type: str
    status: str
    status_reason: str | None
    environment: Environment
    sender: MessageIdentity
    recipient: MessageIdentity
    provider: str | None
    provider_message_id: str | None
    template_name: str | None
    template_id: str | None
    template_version_id: str | None
    template_version: int | None
    media: InboundMessageMediaDescriptor | None
    payload: JSONValue | None
    metadata: JSONValue | None
    error_code: str | None
    error_message: str | None
    provider_error: MessageProviderError | None
    trace_id: str
    created_at: str
    updated_at: str
    redacted_at: str | None
    # Delivery-confirmation timeout stamp. Non-null once the provider accepted the
    # send but no delivery status ever arrived inside the platform's confirmation
    # window; the message is "sent" and stays "sent". Not a status: it clears the
    # moment any status lands, and the message can still be delivered or fail.
    # Always None in sandbox, where statuses are delivered synchronously.
    delivery_unconfirmed_at: str | None


class MessageDetailResponse(MessageSummaryResponse):
    events: list[MessageEventResponse]


class RequestMessageMediaTranscription(TypedDict):
    language: NotRequired[str]


MessageMediaTranscriptStatus: TypeAlias = Literal["pending", "succeeded", "failed"]


class MessageMediaTranscriptResponse(TypedDict):
    id: str
    object: Literal["message_media_transcript"]
    message_id: str
    media_asset_id: str
    status: MessageMediaTranscriptStatus
    provider: str | None
    model: str | None
    language: str | None
    text: str | None
    duration_seconds: int | None
    error_code: str | None
    error_message: str | None
    trace_id: str
    created_at: str
    completed_at: str | None


class TypingIndicatorResponse(TypedDict):
    object: Literal["typing_indicator"]
    message_id: str
    status: Literal["accepted"]


class ListMessagesResponse(TypedDict):
    object: Literal["list"]
    data: list[MessageSummaryResponse]
    has_more: bool
    next_cursor: str | None


WhatsAppTextMessageInput = TypedDict(
    "WhatsAppTextMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
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
        "to": Required[str | StructuredPhoneInput],
        "media": Required[MediaMessagePayload],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTTSMessageInput = TypedDict(
    "WhatsAppTTSMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
        "tts": Required[TTSMediaSource],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppTemplateMessageInput = TypedDict(
    "WhatsAppTemplateMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
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
        "to": Required[str | StructuredPhoneInput],
        "interactive": Required[InteractivePayload],
        "metadata": NotRequired[JSONObject],
    },
    total=False,
)

WhatsAppFlowMessageInput = TypedDict(
    "WhatsAppFlowMessageInput",
    {
        "from": Required[str],
        "to": Required[str | StructuredPhoneInput],
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
