"""Result type for handling success/error outcomes."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass


@dataclass
class Error:
    """Error details container."""
    message: str
    details: Any = None


class Result[T]:
    """
    A result type that can either contain a success value or an error.
    
    Generic type T represents the type of the success value.
    """
    
    def __init__(self, value: T | None = None, error: Error | None = None) -> None:
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        """Whether the result represents a success."""
        return self._error is None

    @property
    def is_error(self) -> bool:
        """Whether the result represents an error."""
        return self._error is not None

    @property
    def value(self) -> T:
        """
        Get the success value.
        
        Raises:
            RuntimeError: If the result represents an error
        """
        if not self.is_success:
            raise RuntimeError("Cannot access value of error Result")
        return self._value

    @property
    def error(self) -> Error:
        """
        Get the error details.
        
        Raises:
            RuntimeError: If the result represents a success
        """
        if not self.is_error:
            raise RuntimeError("Cannot access error of successful Result")
        return self._error

    @classmethod
    def success(cls, value: T) -> Result[T]:
        """Create a success result with the given value."""
        return cls(value=value)

    @classmethod
    def error(cls, message: str, details: Any = None) -> Result[T]:
        """Create an error result with the given message and optional details."""
        return cls(error=Error(message=message, details=details))

    def __str__(self) -> str:
        """String representation of the Result."""
        if self.is_success:
            return f"Result(success={self._value})"
        return f"Result(error={self._error})" 