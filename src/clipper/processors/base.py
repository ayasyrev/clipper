"""Base processor interface for text transformations."""

from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """Abstract base class for all text processors."""

    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process the input text and return transformed text.

        Args:
            text: The input text to process.

        Returns:
            The processed/transformed text.
        """
        pass

    def can_process(self, text: str) -> bool:
        """
        Check if this processor can handle the given text.

        Args:
            text: The input text to check.

        Returns:
            True if this processor can handle the text, False otherwise.
        """
        return True

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this processor."""
        pass

    @property
    def description(self) -> str:
        """Return a description of what this processor does."""
        return f"{self.name} processor"
