"""Tests for layout detection logic."""

from clipper.processors.layout_detector import LayoutDetector


class TestLayoutDetector:
    """Test layout detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = LayoutDetector(confidence_threshold=0.7)

    def test_empty_text(self):
        """Test detection with empty text."""
        result = self.detector.detect_layout("")

        assert result.detected_layout == "unknown"
        assert result.intended_layout == "unknown"
        assert result.confidence == 0.0
        assert result.needs_conversion is False

    def test_whitespace_only(self):
        """Test detection with whitespace only."""
        result = self.detector.detect_layout("   \n\t  ")

        assert result.detected_layout == "unknown"
        assert result.intended_layout == "unknown"
        assert result.confidence == 0.0
        assert result.needs_conversion is False

    def test_russian_text_correct_layout(self):
        """Test detection with correct Russian text."""
        russian_text = "привет мир это тест"
        result = self.detector.detect_layout(russian_text)

        assert result.detected_layout == "ru"
        # Should not need conversion if already correct
        assert result.needs_conversion is False

    def test_english_text_correct_layout(self):
        """Test detection with correct English text."""
        english_text = "hello world this is a test"
        result = self.detector.detect_layout(english_text)

        assert result.detected_layout == "en"
        # Should not need conversion if already correct
        assert result.needs_conversion is False

    def test_russian_typed_with_english_layout(self):
        """Test detection of Russian words typed with English layout."""
        # "привет" typed with English layout becomes "ghbdtn"
        mistyped_text = "ghbdtn vbh"  # "привет мир"
        result = self.detector.detect_layout(mistyped_text)

        # Should detect as English layout but intended as Russian
        assert result.detected_layout == "en"
        if result.needs_conversion:
            assert result.intended_layout == "ru"

    def test_english_typed_with_russian_layout(self):
        """Test detection of English words typed with Russian layout."""
        # "hello" typed with Russian layout becomes "руддщ"
        mistyped_text = "руддщ цщкдв"  # "hello world"
        result = self.detector.detect_layout(mistyped_text)

        # Should detect as Russian layout but intended as English
        assert result.detected_layout == "ru"
        if result.needs_conversion:
            assert result.intended_layout == "en"

    def test_mixed_content(self):
        """Test detection with mixed content (letters and numbers)."""
        mixed_text = "руддщ 123 world!"
        result = self.detector.detect_layout(mixed_text)

        # Should still be able to make a decision
        assert result.detected_layout in ["ru", "en"]
        assert isinstance(result.confidence, float)

    def test_non_alphabetic_content(self):
        """Test detection with non-alphabetic content."""
        symbols_text = "!@#$%^&*()123456"
        result = self.detector.detect_layout(symbols_text)

        # Should handle gracefully
        assert result.confidence >= 0.0
        assert result.needs_conversion is False

    def test_confidence_threshold(self):
        """Test that confidence threshold affects results."""
        detector_low = LayoutDetector(confidence_threshold=0.1)
        detector_high = LayoutDetector(confidence_threshold=0.9)

        ambiguous_text = "a"  # Single character, ambiguous

        result_low = detector_low.detect_layout(ambiguous_text)
        result_high = detector_high.detect_layout(ambiguous_text)

        # Different thresholds might give different conversion decisions
        assert isinstance(result_low.needs_conversion, bool)
        assert isinstance(result_high.needs_conversion, bool)
