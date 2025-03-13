from pydantic import Field
from content_core_sdk.models.base_model import ISerializable

class ContentRequestsPicture(ISerializable):
    service: str | None = Field(None, description="Name of the service", example="twitter_interface")
    feature: str | None = Field(None, description="Producer method name", example="reply_mention")
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation", example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str | None = Field(None, description="ID of the requesting user", example="user_12345")
    character_name: str | None = Field(None, description="Optional name of a character to incorporate into the image generation", example="Harry Potter")
    request_text: str = Field(..., description="Text prompt for image generation (max 100 tokens)", max_length=100, example="A magical castle under a starry night sky")
    height: int = Field(1024, description="Height of the generated image in pixels (more than 200, less than 1440)", ge =200, le=1440, example=1024)
    width: int = Field(1024, description="Width of the generated image in pixels (more than 200, less than 2560)", ge=200, le=2560, example=1024)
    num_inference_steps: int = Field(50, description="Number of denoising steps in the image generation process. More steps lead to better quality but longer generation time.", ge=1, le=100, example=50)
    guidance_scale: int = Field(3, description="Scale factor determining how closely the image follows the text prompt", ge=1, le=100, example=7)

class ContentResponsesPicture(ISerializable):
    service: str | None = Field(None, description="Name of the service", example="twitter_interface")
    feature: str | None = Field(None, description="Producer method name", example="reply_mention") 
    correlation_id: str | None = Field(None, description="Unique ID for request-response correlation", example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str | None = Field(None, description="ID of the requesting user", example="user_12345")
    character_name: str | None = Field(None, description="Name of the character for the image", example="Harry Potter")
    response_text: str = Field(..., description="Response text, containing the IPFS hash link to the generated image", example="QmX7YZzXJKzKbHGYzLvhEh2PtcMPYXcHmx7FqZdHD9xJKv")

