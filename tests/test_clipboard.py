"""Tests for clipboard operations."""

import pytest
from unittest.mock import patch

from clipper.clipboard import (
    get_clipboard_text,
    set_clipboard_text,
    is_clipboard_available,
    ClipboardError,
)


class TestClipboard:
    """Test clipboard operations."""

    @patch("clipper.clipboard.pyperclip.paste")
    def test_get_clipboard_text_success(self, mock_paste):
        """Test successful clipboard text retrieval."""
        mock_paste.return_value = "test text"

        result = get_clipboard_text()

        assert result == "test text"
        mock_paste.assert_called_once()

    @patch("clipper.clipboard.pyperclip.paste")
    def test_get_clipboard_text_none(self, mock_paste):
        """Test clipboard text retrieval when clipboard returns None."""
        mock_paste.return_value = None

        result = get_clipboard_text()

        assert result == ""
        mock_paste.assert_called_once()

    @patch("clipper.clipboard.pyperclip.paste")
    def test_get_clipboard_text_error(self, mock_paste):
        """Test clipboard text retrieval error handling."""
        mock_paste.side_effect = Exception("Clipboard access denied")

        with pytest.raises(ClipboardError) as exc_info:
            get_clipboard_text()

        assert "Failed to read from clipboard" in str(exc_info.value)

    @patch("clipper.clipboard.pyperclip.copy")
    def test_set_clipboard_text_success(self, mock_copy):
        """Test successful clipboard text setting."""
        test_text = "hello world"

        set_clipboard_text(test_text)

        mock_copy.assert_called_once_with(test_text)

    @patch("clipper.clipboard.pyperclip.copy")
    def test_set_clipboard_text_error(self, mock_copy):
        """Test clipboard text setting error handling."""
        mock_copy.side_effect = Exception("Clipboard write failed")

        with pytest.raises(ClipboardError) as exc_info:
            set_clipboard_text("test")

        assert "Failed to write to clipboard" in str(exc_info.value)

    @patch("clipper.clipboard.pyperclip.paste")
    def test_is_clipboard_available_true(self, mock_paste):
        """Test clipboard availability check when available."""
        mock_paste.return_value = "test"

        result = is_clipboard_available()

        assert result is True
        mock_paste.assert_called_once()

    @patch("clipper.clipboard.pyperclip.paste")
    def test_is_clipboard_available_false(self, mock_paste):
        """Test clipboard availability check when not available."""
        mock_paste.side_effect = Exception("No clipboard")

        result = is_clipboard_available()

        assert result is False
        mock_paste.assert_called_once()
