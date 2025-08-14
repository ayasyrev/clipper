"""Tests for the main CLI interface."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from clipper import main


class TestMainCLI:
    """Test the main CLI interface."""

    @patch("clipper.is_clipboard_available")
    @patch("clipper.ProcessingEngine")
    def test_main_success(self, mock_engine_class, mock_clipboard_available):
        """Test successful main execution."""
        # Setup mocks
        mock_clipboard_available.return_value = True
        mock_engine = MagicMock()
        mock_engine.process_clipboard.return_value = True
        mock_engine_class.return_value = mock_engine

        # Mock sys.argv to avoid argument parsing issues
        with patch.object(sys, "argv", ["clipper"]):
            # Should not raise SystemExit
            main()

        # Verify calls
        mock_clipboard_available.assert_called_once()
        mock_engine_class.assert_called_once()
        mock_engine.process_clipboard.assert_called_once()

    @patch("clipper.is_clipboard_available")
    def test_main_clipboard_unavailable(self, mock_clipboard_available):
        """Test main execution when clipboard is unavailable."""
        mock_clipboard_available.return_value = False

        captured_stderr = StringIO()

        with patch.object(sys, "argv", ["clipper"]):
            with patch("sys.stderr", captured_stderr):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        stderr_content = captured_stderr.getvalue()
        assert "Clipboard is not available" in stderr_content

    @patch("clipper.is_clipboard_available")
    @patch("clipper.ProcessingEngine")
    def test_main_processing_failure(self, mock_engine_class, mock_clipboard_available):
        """Test main execution when processing fails."""
        # Setup mocks
        mock_clipboard_available.return_value = True
        mock_engine = MagicMock()
        mock_engine.process_clipboard.return_value = False  # Processing failed
        mock_engine_class.return_value = mock_engine

        with patch.object(sys, "argv", ["clipper"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

    def test_main_version_argument(self):
        """Test --version argument."""
        with patch.object(sys, "argv", ["clipper", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # argparse exits with code 0 for --version
        assert exc_info.value.code == 0

    def test_main_help_argument(self):
        """Test --help argument."""
        with patch.object(sys, "argv", ["clipper", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # argparse exits with code 0 for --help
        assert exc_info.value.code == 0

    @patch("clipper.is_clipboard_available")
    @patch("clipper.ProcessingEngine")
    def test_main_verbose_argument(self, mock_engine_class, mock_clipboard_available):
        """Test -v/--verbose argument."""
        # Setup mocks
        mock_clipboard_available.return_value = True
        mock_engine = MagicMock()
        mock_engine.process_clipboard.return_value = True
        mock_engine_class.return_value = mock_engine

        # Test short form
        with patch.object(sys, "argv", ["clipper", "-v"]):
            main()

        # Test long form
        with patch.object(sys, "argv", ["clipper", "--verbose"]):
            main()

        # Both should succeed (verbose currently doesn't change behavior)
        assert mock_engine.process_clipboard.call_count == 2
