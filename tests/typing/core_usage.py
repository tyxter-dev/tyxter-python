from __future__ import annotations

from typing_extensions import assert_type

from tyxter import Tyxter
from tyxter.types import (
    CreateMessageRequest,
    InboundMessageMediaDescriptor,
    InboundMessageMediaFailed,
    InboundMessageMediaFailure,
    ListMediaAssetsResponse,
    ListMessagesResponse,
    MediaAssetDownloadResponse,
    MessageBatchPacingResponse,
    MessageBatchResponse,
    MessageDetailResponse,
    MessageMediaTranscriptResponse,
    MessageResponse,
    MessageSummaryResponse,
    NativePixOrderDetailsMessagePayload,
    PhoneNumberResponse,
    ProviderConnectionResponse,
    ProviderCredentialSetupSessionCompletedOpenAISttResult,
    ProviderCredentialSetupSessionResponse,
    ProviderCredentialSetupSessionResult,
    ProviderCredentialSetupSttProvider,
    RequestMessageMediaTranscription,
    TypingIndicatorResponse,
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
    assert_type(
        client.messages.list(direction="inbound", include="payload"),
        ListMessagesResponse,
    )
    assert_type(client.messages.retrieve("msg_123"), MessageDetailResponse)
    assert_type(client.messages.cancel("msg_123"), MessageDetailResponse)

    transcription: RequestMessageMediaTranscription = {"language": "pt"}
    assert_type(
        client.messages.request_transcription("msg_123", transcription),
        MessageMediaTranscriptResponse,
    )
    assert_type(
        client.messages.retrieve_transcription("msg_123"),
        MessageMediaTranscriptResponse,
    )
    assert_type(client.messages.typing("msg_123"), TypingIndicatorResponse)
    assert_type(client.media.list(source="inbound_provider"), ListMediaAssetsResponse)
    assert_type(client.media.create_download_url("mda_123"), MediaAssetDownloadResponse)
    assert_type(
        client.provider_credential_setup_sessions.create({"target": "openai.stt"}),
        ProviderCredentialSetupSessionResponse,
    )
    setup_result = client.provider_credential_setup_sessions.create_result({"target": "openai.stt"})
    assert_type(
        setup_result,
        ProviderCredentialSetupSessionResult,
    )
    retrieved_setup_result = client.provider_credential_setup_sessions.retrieve_result("pcs_123")
    assert_type(retrieved_setup_result, ProviderCredentialSetupSessionResult)
    provider_credential_setup_result_narrowing(setup_result)
    provider_credential_setup_result_narrowing(retrieved_setup_result)

    order_details: NativePixOrderDetailsMessagePayload = {
        "type": "order_details",
        "body": {"text": "Review your order"},
        "action": {
            "name": "review_and_pay",
            "parameters": {
                "reference_id": "order_123",
                "type": "physical-goods",
                "payment_type": "br",
                "payment_settings": (
                    {
                        "type": "pix_dynamic_code",
                        "pix_dynamic_code": {
                            "code": "000201010212",
                            "merchant_name": "Tyxter Store",
                            "key": "merchant@example.com",
                            "key_type": "EMAIL",
                        },
                    },
                ),
                "currency": "BRL",
                "total_amount": {"value": 12990, "offset": 100},
            },
        },
    }
    client.whatsapp.send_interactive(
        {
            "from": "pn_123",
            "to": {"country_calling_code": "55", "national_number": "11999999999"},
            "interactive": order_details,
        }
    )


def a1_response_shapes(
    batch: MessageBatchResponse,
    message: MessageSummaryResponse,
    media: InboundMessageMediaDescriptor,
    phone_number: PhoneNumberResponse,
    provider_connection: ProviderConnectionResponse,
) -> None:
    assert_type(batch["pacing"], MessageBatchPacingResponse | None)
    assert_type(message["status_reason"], str | None)
    assert_type(message["media"], InboundMessageMediaDescriptor | None)
    assert_type(message["redacted_at"], str | None)
    assert_type(media["asset_id"], str)
    if media["status"] == "failed":
        assert_type(media, InboundMessageMediaFailed)
        assert_type(media["failure"], InboundMessageMediaFailure)
    assert_type(phone_number["remaining_messaging_allowance_estimate"], int | None)
    if "display_phone_number" in provider_connection:
        assert_type(provider_connection["display_phone_number"], str | None)
    if "suspension_reason" in provider_connection:
        assert_type(provider_connection["suspension_reason"], str | None)


def provider_credential_setup_result_narrowing(
    result: ProviderCredentialSetupSessionResult,
) -> None:
    if result["status"] == "completed" and result["target"] == "openai.stt":
        assert_type(result, ProviderCredentialSetupSessionCompletedOpenAISttResult)
        assert_type(result["completed_stt_provider"], ProviderCredentialSetupSttProvider)
        assert_type(result["completed_tts_provider"], None)


def create(client: Tyxter) -> ProviderCredentialSetupSessionResponse:
    return client.provider_credential_setup_sessions.create({"target": "openai.tts"})


def mutate_legacy_provider_credential_setup_session(
    result: ProviderCredentialSetupSessionResponse,
) -> None:
    result["target"] = "openai.stt"
    result["status"] = "completed"
    result["completed_provider_connection_id"] = "pcn_123"
    result["completed_tts_provider"] = "openai"
    result["completed_stt_provider"] = "openai"
