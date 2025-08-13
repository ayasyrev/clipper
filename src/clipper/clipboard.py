"""Cross-platform clipboard operations."""

import pyperclip


class ClipboardError(Exception):
    """Raised when clipboard operations fail."""

    pass


def get_clipboard_text() -> str:
    """
    Get text from the system clipboard.

    Returns:
        The text content from clipboard, empty string if clipboard is empty.

    Raises:
        ClipboardError: If clipboard access fails.
    """
    try:
        text = pyperclip.paste()
        return text if text is not None else ""
    except Exception as e:
        raise ClipboardError(f"Failed to read from clipboard: {e}") from e


def set_clipboard_text(text: str) -> None:
    """
    Set text to the system clipboard.

    Args:
        text: The text to copy to clipboard.

    Raises:
        ClipboardError: If clipboard access fails.
    """
    try:
        pyperclip.copy(text)
    except Exception as e:
        raise ClipboardError(f"Failed to write to clipboard: {e}") from e


def is_clipboard_available() -> bool:
    """
    Check if clipboard is available and accessible.

    Returns:
        True if clipboard can be accessed, False otherwise.
    """
    try:
        # Try to read from clipboard to test access
        pyperclip.paste()
        return True
    except Exception:
        return False
