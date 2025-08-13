"""Tests for the main processing engine."""

from unittest.mock import patch
from io import StringIO

from clipper.engine import ProcessingEngine
from clipper.processors.base import BaseProcessor
from clipper.clipboard import ClipboardError


class MockProcessor(BaseProcessor):
    """Mock processor for testing."""

    def __init__(self, name="Mock", can_process_return=True, process_return=None):
        self._name = name
        self._can_process_return = can_process_return
        self._process_return = process_return

    @property
    def name(self) -> str:
        return self._name

    def can_process(self, text: str) -> bool:
        return self._can_process_return

    def process(self, text: str) -> str:
        if self._process_return is not None:
            return self._process_return
        return text + "_processed"


class TestProcessingEngine:
    """Test the main processing engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ProcessingEngine()

    def test_engine_initialization(self):
        """Test that engine initializes with default processors."""
        processors = self.engine.get_available_processors()

        assert len(processors) > 0
        assert "Layout Converter" in processors

    def test_register_processor(self):
        """Test registering a new processor."""
        mock_processor = MockProcessor(name="Test Processor")

        self.engine.register_processor(mock_processor)
        processors = self.engine.get_available_processors()

        assert "Test Processor" in processors

    @patch("clipper.engine.get_clipboard_text")
    @patch("clipper.engine.set_clipboard_text")
    def test_process_clipboard_success(self, mock_set_clipboard, mock_get_clipboard):
        """Test successful clipboard processing."""
        # Setup
        mock_get_clipboard.return_value = "test input"
        mock_processor = MockProcessor(process_return="test output")

        # Clear default processors and add our mock
        self.engine.processors = [mock_processor]

        # Capture stderr to check messages
        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        # Verify
        assert result is True
        mock_get_clipboard.assert_called_once()
        mock_set_clipboard.assert_called_once_with("test output")

        stderr_content = captured_stderr.getvalue()
        assert "successfully" in stderr_content

    @patch("clipper.engine.get_clipboard_text")
    def test_process_clipboard_empty_text(self, mock_get_clipboard):
        """Test processing with empty clipboard."""
        mock_get_clipboard.return_value = ""

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is False
        stderr_content = captured_stderr.getvalue()
        assert "empty" in stderr_content.lower()

    @patch("clipper.engine.get_clipboard_text")
    def test_process_clipboard_whitespace_only(self, mock_get_clipboard):
        """Test processing with whitespace-only clipboard."""
        mock_get_clipboard.return_value = "   \n\t  "

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is False
        stderr_content = captured_stderr.getvalue()
        assert (
            "empty" in stderr_content.lower() or "whitespace" in stderr_content.lower()
        )

    @patch("clipper.engine.get_clipboard_text")
    def test_process_clipboard_no_suitable_processor(self, mock_get_clipboard):
        """Test processing when no processor can handle the text."""
        mock_get_clipboard.return_value = "test input"
        mock_processor = MockProcessor(can_process_return=False)

        # Replace default processors with our mock that can't process
        self.engine.processors = [mock_processor]

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is False
        stderr_content = captured_stderr.getvalue()
        assert "No processor available" in stderr_content

    @patch("clipper.engine.get_clipboard_text")
    @patch("clipper.engine.set_clipboard_text")
    def test_process_clipboard_no_changes(self, mock_set_clipboard, mock_get_clipboard):
        """Test processing when text doesn't change."""
        test_text = "test input"
        mock_get_clipboard.return_value = test_text
        mock_processor = MockProcessor(process_return=test_text)  # Same as input

        self.engine.processors = [mock_processor]

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is True
        # Should not call set_clipboard since text didn't change
        mock_set_clipboard.assert_not_called()

        stderr_content = captured_stderr.getvalue()
        assert "No changes needed" in stderr_content

    @patch("clipper.engine.get_clipboard_text")
    def test_process_clipboard_error(self, mock_get_clipboard):
        """Test processing with clipboard error."""
        mock_get_clipboard.side_effect = ClipboardError("Clipboard access denied")

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is False
        stderr_content = captured_stderr.getvalue()
        assert "Clipboard error" in stderr_content

    @patch("clipper.engine.get_clipboard_text")
    def test_process_clipboard_processing_error(self, mock_get_clipboard):
        """Test processing with general processing error."""
        mock_get_clipboard.return_value = "test input"

        # Create processor that raises an exception
        class ErrorProcessor(BaseProcessor):
            @property
            def name(self):
                return "Error Processor"

            def can_process(self, text):
                return True

            def process(self, text):
                raise ValueError("Processing failed")

        self.engine.processors = [ErrorProcessor()]

        captured_stderr = StringIO()

        with patch("sys.stderr", captured_stderr):
            result = self.engine.process_clipboard()

        assert result is False
        stderr_content = captured_stderr.getvalue()
        assert "Processing error" in stderr_content

    def test_find_processor(self):
        """Test finding appropriate processor."""
        # Create processors with different capabilities
        processor1 = MockProcessor(name="Processor1", can_process_return=False)
        processor2 = MockProcessor(name="Processor2", can_process_return=True)
        processor3 = MockProcessor(name="Processor3", can_process_return=True)

        self.engine.processors = [processor1, processor2, processor3]

        # Should return first processor that can handle the text
        found = self.engine._find_processor("test text")

        assert found is processor2  # First one that returns True

    def test_find_processor_none_available(self):
        """Test finding processor when none are available."""
        processor = MockProcessor(can_process_return=False)
        self.engine.processors = [processor]

        found = self.engine._find_processor("test text")

        assert found is None
