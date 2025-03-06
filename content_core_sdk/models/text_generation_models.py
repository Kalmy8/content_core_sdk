from pydantic import Field

from content_core_sdk.models.base_model import ISerializable


class ContentRequestsText(ISerializable):
    service: str | None = Field(None, description="Name of the service")
    feature: str | None = Field(None, description="Producer method name")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation")
    user_id: str | None = Field(None, description="ID of the requesting user")
    character_name: str = Field(None, description="Name of the character for text generation")
    request_text: str = Field(..., description="Text prompt for generating the answer")
    task_description: str = Field(..., description="Additional context for the text generation task")

class ContentResponsesText(ISerializable):
    service: str | None = Field(None, description="Name of the service")
    feature: str | None = Field(None, description="Producer method name")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation")
    user_id: str | None = Field(None, description="ID of the requesting user")
    character_name: str | None = Field(None, description="Name of the character for text generation")
    response_text: str = Field(..., description="AI - generated text")
