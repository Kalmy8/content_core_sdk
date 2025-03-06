import json
from abc import ABC
from typing import Self
from pydantic import BaseModel, ValidationError

class ISerializable(BaseModel, ABC):

    def to_bytes(self) -> bytes:
        """Serialize the model to UTF-8 encoded JSON bytes"""
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """Deserialize bytes to model instance with validation"""
        try:
            # Decode bytes and parse JSON
            json_data = json.loads(data.decode("utf-8"))
            # Validate against model schema
            return cls.model_validate(json_data)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError("Invalid byte format - must be UTF-8 encoded JSON") from e
        except ValidationError as e:
            raise ValueError(f"Validation error: {e.errors()}") from e
