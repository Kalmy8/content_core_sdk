from pydantic import Field

from content_core_sdk.models.base_model import ISerializable


class ContentRequestsText(ISerializable):
    service: str | None = Field(None, description="Name of the service", example="twitter_interface")
    feature: str | None = Field(None, description="Producer method name", example="reply_tweet")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation", example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str | None = Field(None, description="ID of the requesting user", example="user_12345")
    character_name: str = Field(None, description="Name of the character for text generation", example="Sherlock Holmes")
    request_text: str = Field(..., description="Text prompt for generating the answer", example="What's your approach to solving difficult mysteries?")
    task_description: str = Field(..., description="Additional context for the text generation task", example="Respond as Sherlock Holmes, the famous detective known for logical deduction.")

class ContentResponsesText(ISerializable):
    service: str | None = Field(None, description="Name of the service", example="twitter_interface")
    feature: str | None = Field(None, description="Producer method name", example="reply_tweet")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation", example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str | None = Field(None, description="ID of the requesting user", example="user_12345")
    character_name: str | None = Field(None, description="Name of the character for text generation", example="Sherlock Holmes")
    response_text: str = Field(..., description="AI-generated text", example="Elementary, my dear friend. The approach to solving difficult mysteries always begins with careful observation. One must train oneself to see what others merely look at.")