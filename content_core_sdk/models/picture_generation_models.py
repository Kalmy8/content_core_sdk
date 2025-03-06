from pydantic import Field
from content_core_sdk.models.base_model import ISerializable

class ContentRequestsPicture(ISerializable):
    service: str | None = Field(None, description="Name of the service")
    feature: str | None = Field(None, description="Producer method name")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation")
    user_id: str | None = Field(None, description="ID of the requesting user")
    character_name: str | None = Field(None, description="Name of the character for the image")
    request_text: str = Field(..., description="Text prompt for generating the image")
    task_description: str = Field(..., description="Additional context for the image generation task")

class ContentResponsesPicture(ISerializable):
    service: str | None = Field(None, description="Name of the service")
    feature: str | None = Field(None, description="Producer method name")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation")
    user_id: str | None = Field(None, description="ID of the requesting user")
    character_name: str | None = Field(None, description="Name of the character for the image")
    response_text: str = Field(..., description="Response text, containing the IPFS hash link to the generated image")

