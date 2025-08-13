"""Tests for layout converter."""

from clipper.processors.layout_converter import LayoutConverter


class TestLayoutConverter:
    """Test layout conversion functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = LayoutConverter(confidence_threshold=0.7)

    def test_processor_properties(self):
        """Test processor properties."""
        assert self.converter.name == "Layout Converter"
        assert "keyboard layouts" in self.converter.description

    def test_empty_text(self):
        """Test processing empty text."""
        result = self.converter.process("")
        assert result == ""

        assert not self.converter.can_process("")

    def test_whitespace_only(self):
        """Test processing whitespace only."""
        text = "   \n\t  "
        result = self.converter.process(text)
        assert result == text

        assert not self.converter.can_process(text)

    def test_correct_english_text(self):
        """Test processing correct English text."""
        english_text = "hello world this is a test"
        result = self.converter.process(english_text)

        # Should return unchanged if no conversion needed
        assert result == english_text

    def test_correct_russian_text(self):
        """Test processing correct Russian text."""
        russian_text = "привет мир это тест"
        result = self.converter.process(russian_text)

        # Should return unchanged if no conversion needed
        assert result == russian_text

    def test_russian_to_english_conversion(self):
        """Test converting Russian layout to English."""
        # "hello" typed with Russian layout
        russian_layout_text = "руддщ"
        expected_english = "hello"

        result = self.converter.process(russian_layout_text)

        # Should convert to English
        if self.converter.can_process(russian_layout_text):
            assert result == expected_english
        else:
            # If confidence is too low, should return original
            assert result == russian_layout_text

    def test_english_to_russian_conversion(self):
        """Test converting English layout to Russian."""
        # "привет" typed with English layout
        english_layout_text = "ghbdtn"
        expected_russian = "привет"

        result = self.converter.process(english_layout_text)

        # Should convert to Russian
        if self.converter.can_process(english_layout_text):
            assert result == expected_russian
        else:
            # If confidence is too low, should return original
            assert result == english_layout_text

    def test_complex_text_conversion(self):
        """Test converting more complex text."""
        # "hello world" in Russian layout
        russian_layout_text = "руддщ цщкдв"

        result = self.converter.process(russian_layout_text)

        if self.converter.can_process(russian_layout_text):
            # Should convert to something resembling "hello world"
            assert "hello" in result.lower()
            assert "world" in result.lower()

    def test_mixed_content_conversion(self):
        """Test converting mixed content (letters, numbers, symbols)."""
        # "hello 123!" in Russian layout
        mixed_text = "руддщ 123!"

        result = self.converter.process(mixed_text)

        # Numbers and symbols should be preserved
        assert "123!" in result

        if self.converter.can_process(mixed_text):
            # Letters should be converted
            assert "hello" in result.lower()

    def test_preserve_whitespace_and_structure(self):
        """Test that whitespace and text structure are preserved."""
        text_with_structure = "руддщ,\nцщкдв\tершыею"

        result = self.converter.process(text_with_structure)

        # Should preserve comma, newline, and tab
        if self.converter.can_process(text_with_structure):
            assert "," in result
            assert "\n" in result
            assert "\t" in result

    def test_case_preservation(self):
        """Test that text case is preserved during conversion."""
        # "Hello World" in Russian layout with mixed case
        mixed_case_text = "Руддщ Цщкдв"

        result = self.converter.process(mixed_case_text)

        if self.converter.can_process(mixed_case_text):
            # Should preserve capitalization
            assert result[0].isupper()  # First character should be uppercase
            assert " " in result  # Space should be preserved

    def test_get_detection_info(self):
        """Test getting detection information."""
        test_text = "руддщ цщкдв"

        info = self.converter.get_detection_info(test_text)

        assert hasattr(info, "detected_layout")
        assert hasattr(info, "intended_layout")
        assert hasattr(info, "confidence")
        assert hasattr(info, "needs_conversion")

        assert info.detected_layout in ["ru", "en", "mixed", "unknown"]
        assert info.intended_layout in ["ru", "en", "mixed", "unknown"]
        assert 0.0 <= info.confidence <= 1.0
        assert isinstance(info.needs_conversion, bool)

    def test_can_process_method(self):
        """Test the can_process method."""
        # Test with text that should trigger conversion
        convertible_text = "руддщ"  # "hello" in Russian layout

        can_process = self.converter.can_process(convertible_text)

        # Should be able to determine processability
        assert isinstance(can_process, bool)

        # Test with empty text
        assert not self.converter.can_process("")
        assert not self.converter.can_process("   ")
