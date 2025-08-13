"""Layout converter for fixing keyboard layout issues."""

from typing import Dict
from .base import BaseProcessor
from .layout_detector import LayoutDetector, LayoutDetectionResult
from ..mappings.layouts import RU_TO_EN_MAPPING, EN_TO_RU_MAPPING


class LayoutConverter(BaseProcessor):
    """Processor that converts text between Russian and English keyboard layouts."""

    def __init__(self, confidence_threshold: float = 0.3):
        self.detector = LayoutDetector(confidence_threshold)
        self._mappings = {
            "ru_to_en": RU_TO_EN_MAPPING,
            "en_to_ru": EN_TO_RU_MAPPING,
        }

    @property
    def name(self) -> str:
        return "Layout Converter"

    @property
    def description(self) -> str:
        return "Converts text between Russian and English keyboard layouts"

    def can_process(self, text: str) -> bool:
        """Check if text needs layout conversion."""
        if not text.strip():
            return False

        detection = self.detector.detect_layout(text)
        return detection.needs_conversion

    def process(self, text: str) -> str:
        """
        Process text by converting keyboard layout if needed.

        Args:
            text: Input text that may have wrong keyboard layout.

        Returns:
            Text with corrected keyboard layout.
        """
        if not text.strip():
            return text

        detection = self.detector.detect_layout(text)

        if not detection.needs_conversion:
            return text

        # Determine conversion direction
        if detection.detected_layout == "ru" and detection.intended_layout == "en":
            mapping = self._mappings["ru_to_en"]
        elif detection.detected_layout == "en" and detection.intended_layout == "ru":
            mapping = self._mappings["en_to_ru"]
        else:
            # If we're not confident about the conversion, return original text
            return text

        return self._convert_text(text, mapping)

    def _convert_text(self, text: str, mapping: Dict[str, str]) -> str:
        """Convert text using the provided character mapping."""
        result = []
        for char in text:
            # Convert character if mapping exists, otherwise keep original
            result.append(mapping.get(char, char))
        return "".join(result)

    def get_detection_info(self, text: str) -> LayoutDetectionResult:
        """
        Get detailed information about layout detection for debugging.

        Args:
            text: Text to analyze.

        Returns:
            LayoutDetectionResult with detection details.
        """
        return self.detector.detect_layout(text)
