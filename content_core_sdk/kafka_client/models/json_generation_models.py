from content_core_sdk.kafka_client.models.base_model import ISerializable
from pydantic import BaseModel


class ContentRequestsJson(BaseModel, ISerializable):
    service: str | None = None
    feature: str | None = None
    correlation_id: str | None = None
    user_id: str | None = None
    character_name: str
    request_text: str
    sys_prompt: str


class ContentResponsesJson(BaseModel, ISerializable):
    service: str | None = None
    feature: str | None = None
    correlation_id: str | None = None
    character_name: str | None = None
    user_id: str | None = None
    response_text: str
