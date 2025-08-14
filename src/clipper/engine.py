"""Main processing engine for clipboard operations."""

import sys
from pathlib import Path
from typing import List, Optional
from .clipboard import get_clipboard_text, set_clipboard_text, ClipboardError
from .processors.base import BaseProcessor
from .processors.layout_converter import LayoutConverter


class ProcessingEngine:
    """Main engine that orchestrates clipboard processing."""

    def __init__(self) -> None:
        self.processors: List[BaseProcessor] = []
        self._register_default_processors()
        app_dir = Path.home() / ".clipper"
        app_dir.mkdir(exist_ok=True)
        self._undo_file = app_dir / "undo_state"

    def _truncate_text(self, text: str, max_chars: int = 10) -> str:
        """Truncate text to specified number of characters for preview."""
        return text[:max_chars] if len(text) > max_chars else text

    def _save_clipboard_for_undo(self, text: str) -> None:
        """Save clipboard content for undo functionality."""
        try:
            self._undo_file.write_text(text, encoding="utf-8")
        except Exception as e:
            # Don't fail the main operation if undo save fails
            print(f"Warning: Could not save undo state: {e}", file=sys.stderr)

    def _load_clipboard_for_undo(self) -> Optional[str]:
        """Load clipboard content for undo functionality."""
        try:
            if self._undo_file.exists():
                return self._undo_file.read_text(encoding="utf-8")
        except Exception:
            pass
        return None

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

            # If no specific processor is found, use Layout Converter as default
            if not processor:
                processor = self._get_default_processor()

            # Process the text
            processed_text = processor.process(text)

            # Check if text was actually changed
            if processed_text == text:
                text_preview = self._truncate_text(text)
                print(f'no need to convert: "{text_preview}"', file=sys.stderr)
                return True

            # Save original text for undo before modifying clipboard
            self._save_clipboard_for_undo(text)

            # Set processed text back to clipboard
            set_clipboard_text(processed_text)

            # Show concise success message with text preview
            original_preview = self._truncate_text(text)
            processed_preview = self._truncate_text(processed_text)
            print(
                f'done: "{original_preview}" --> "{processed_preview}"', file=sys.stderr
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

    def _get_default_processor(self) -> BaseProcessor:
        """Get the default processor (Layout Converter) for fallback processing."""
        return LayoutConverter()

    def register_processor(self, processor: BaseProcessor) -> None:
        """Register a new processor."""
        self.processors.append(processor)

    def get_available_processors(self) -> List[str]:
        """Get names of all available processors."""
        return [processor.name for processor in self.processors]

    def process_clipboard_interactive(self) -> bool:
        """
        Process clipboard content with user confirmation.

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

            # If no specific processor is found, use Layout Converter as default
            if not processor:
                processor = self._get_default_processor()

            # Process the text
            processed_text = processor.process(text)

            # Check if text was actually changed
            if processed_text == text:
                text_preview = self._truncate_text(text)
                print(f'no need to convert: "{text_preview}"', file=sys.stderr)
                return True

            # Show preview and ask for confirmation
            original_preview = self._truncate_text(text)
            processed_preview = self._truncate_text(processed_text)
            print(
                f'Proposed conversion: "{original_preview}" --> "{processed_preview}"'
            )

            try:
                response = input("Proceed with conversion? [y/N]: ").strip().lower()
                if response not in ("y", "yes"):
                    print("Conversion cancelled.", file=sys.stderr)
                    return True
            except (EOFError, KeyboardInterrupt):
                print("\nConversion cancelled.", file=sys.stderr)
                return True

            # Save original text for undo before modifying clipboard
            self._save_clipboard_for_undo(text)

            # Set processed text back to clipboard
            set_clipboard_text(processed_text)

            # Show success message
            print(
                f'done: "{original_preview}" --> "{processed_preview}"', file=sys.stderr
            )
            return True

        except ClipboardError as e:
            print(f"Clipboard error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Processing error: {e}", file=sys.stderr)
            return False

    def dry_run(self) -> bool:
        """
        Show clipboard content and proposed changes without modifying clipboard.

        Returns:
            True if dry run was successful, False otherwise.
        """
        try:
            # Get text from clipboard
            text = get_clipboard_text()

            print("=== CLIPBOARD CONTENT ===")
            if not text.strip():
                print("(empty or whitespace only)")
                return True
            else:
                print(text)

            print("\n=== PROPOSAL ===")

            # Find a processor that can handle the text
            processor = self._find_processor(text)

            if not processor:
                print("No processor available for this text.")
                return True

            # Process the text to get proposed changes
            processed_text = processor.process(text)

            # Check if text would be changed
            if processed_text == text:
                print("No changes needed.")
            else:
                print(f"Processor: {processor.name}")
                print("Proposed changes:")
                print(processed_text)

            return True

        except ClipboardError as e:
            print(f"Clipboard error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Processing error: {e}", file=sys.stderr)
            return False

    def undo(self) -> bool:
        """
        Restore previous clipboard content.

        Returns:
            True if undo was successful, False otherwise.
        """
        try:
            # Load previous clipboard content
            previous_content = self._load_clipboard_for_undo()

            if previous_content is None:
                print("No previous clipboard content to restore.", file=sys.stderr)
                return False

            # Set previous content back to clipboard
            set_clipboard_text(previous_content)

            # Show success message with preview
            restored_preview = self._truncate_text(previous_content)
            print(f'restored: "{restored_preview}"', file=sys.stderr)
            return True

        except ClipboardError as e:
            print(f"Clipboard error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Undo error: {e}", file=sys.stderr)
            return False
