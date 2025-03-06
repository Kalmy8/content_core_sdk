from enum import Enum


class KafkaTopics(str, Enum):
    CONTENT_REQUESTS_TEXT = "content_requests_text"
    CONTENT_RESPONSES_TEXT = "content_responses_text"
    CONTENT_REQUESTS_JSON = "content_requests_json"
    CONTENT_RESPONSES_JSON = "content_responses_json"
    CONTENT_REQUESTS_PICTURE = "content_requests_picture"
    CONTENT_RESPONSES_PICTURE = "content_responses_picture"


