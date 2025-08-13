"""Main processing engine for clipboard operations."""

import sys
from typing import List, Optional
from .clipboard import get_clipboard_text, set_clipboard_text, ClipboardError
from .processors.base import BaseProcessor
from .processors.layout_converter import LayoutConverter


class ProcessingEngine:
    """Main engine that orchestrates clipboard processing."""

    def __init__(self) -> None:
        self.processors: List[BaseProcessor] = []
        self._register_default_processors()

    def _register_default_processors(self) -> None:
        """Register default processors."""
        self.processors.append(LayoutConverter())

    def process_clipboard(self) -> bool:
        """
        Process clipboard content with available processors.

        Returns:
            True if processing was successful, False otherwise.
        """
        try:
            # Get text from clipboard
            text = get_clipboard_text()

            if not text.strip():
                print(
                    "Clipboard is empty or contains only whitespace.", file=sys.stderr
                )
                return False

            # Find a processor that can handle the text
            processor = self._find_processor(text)

            if not processor:
                print("No processor available for this text.", file=sys.stderr)
                return False

            # Process the text
            processed_text = processor.process(text)

            # Check if text was actually changed
            if processed_text == text:
                print("Text analysis completed. No changes needed.", file=sys.stderr)
                return True

            # Set processed text back to clipboard
            set_clipboard_text(processed_text)
            print(
                f"Text processed successfully with {processor.name}.", file=sys.stderr
            )
            return True

        except ClipboardError as e:
            print(f"Clipboard error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Processing error: {e}", file=sys.stderr)
            return False

    def _find_processor(self, text: str) -> Optional[BaseProcessor]:
        """Find the first processor that can handle the given text."""
        for processor in self.processors:
            if processor.can_process(text):
                return processor
        return None

    def register_processor(self, processor: BaseProcessor) -> None:
        """Register a new processor."""
        self.processors.append(processor)

    def get_available_processors(self) -> List[str]:
        """Get names of all available processors."""
        return [processor.name for processor in self.processors]
