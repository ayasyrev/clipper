"""Layout detection logic for identifying keyboard layout issues."""

import re
from typing import Dict
from dataclasses import dataclass

from ..mappings.layouts import (
    COMMON_RUSSIAN_WORDS,
    COMMON_ENGLISH_WORDS,
    RUSSIAN_CHAR_FREQUENCY,
    ENGLISH_CHAR_FREQUENCY,
    RU_TO_EN_MAPPING,
    EN_TO_RU_MAPPING,
)


@dataclass
class LayoutDetectionResult:
    """Result of layout detection analysis."""

    detected_layout: str  # 'ru', 'en', or 'mixed'
    intended_layout: str  # 'ru', 'en', or 'unknown'
    confidence: float  # 0.0 to 1.0
    needs_conversion: bool


class LayoutDetector:
    """Detects keyboard layout and determines if conversion is needed."""

    def __init__(self, confidence_threshold: float = 0.3):
        self.confidence_threshold = confidence_threshold

    def detect_layout(self, text: str) -> LayoutDetectionResult:
        """
        Detect the current layout and intended layout of the text.

        Args:
            text: Input text to analyze.

        Returns:
            LayoutDetectionResult with detection information.
        """
        if not text.strip():
            return LayoutDetectionResult(
                detected_layout="unknown",
                intended_layout="unknown",
                confidence=0.0,
                needs_conversion=False,
            )

        # First check: What layout do the characters suggest?
        ru_char_score = self._calculate_frequency_score(text, "ru")
        en_char_score = self._calculate_frequency_score(text, "en")

        # Determine apparent layout based on character analysis
        apparent_layout = "ru" if ru_char_score > en_char_score else "en"

        # Second check: If we convert, do we get meaningful words?
        ru_to_en_word_score = self._check_common_words_after_conversion(
            text, "ru_to_en"
        )
        en_to_ru_word_score = self._check_common_words_after_conversion(
            text, "en_to_ru"
        )

        # Third check: Are there already meaningful words in the current text?
        current_ru_words = self._check_current_words(text, "ru")
        current_en_words = self._check_current_words(text, "en")

        # Decision logic: conversion is needed if:
        # 1. Converting gives better word scores than current text
        # 2. The conversion score is above threshold

        needs_conversion = False
        intended_layout = apparent_layout
        confidence = max(ru_char_score, en_char_score)

        # Check if Russian->English conversion makes sense
        if (
            ru_to_en_word_score > current_en_words
            and ru_to_en_word_score > current_ru_words
            and ru_to_en_word_score >= self.confidence_threshold
        ):
            needs_conversion = True
            intended_layout = "en"
            confidence = ru_to_en_word_score

        # Check if English->Russian conversion makes sense
        elif (
            en_to_ru_word_score > current_ru_words
            and en_to_ru_word_score > current_en_words
            and en_to_ru_word_score >= self.confidence_threshold
        ):
            needs_conversion = True
            intended_layout = "ru"
            confidence = en_to_ru_word_score

        return LayoutDetectionResult(
            detected_layout=apparent_layout,
            intended_layout=intended_layout,
            confidence=confidence,
            needs_conversion=needs_conversion,
        )

    def _calculate_frequency_score(self, text: str, language: str) -> float:
        """Calculate character frequency score for a language."""
        char_freq = (
            RUSSIAN_CHAR_FREQUENCY if language == "ru" else ENGLISH_CHAR_FREQUENCY
        )

        # Count characters in text
        char_counts: Dict[str, int] = {}
        total_chars = 0

        for char in text.lower():
            if char.isalpha():
                char_counts[char] = char_counts.get(char, 0) + 1
                total_chars += 1

        if total_chars == 0:
            return 0.0

        # Calculate score based on expected frequency
        score = 0.0
        for char, count in char_counts.items():
            if char in char_freq:
                expected_freq = char_freq[char] / 100.0
                actual_freq = count / total_chars
                # Higher score for characters that match expected frequency
                score += min(expected_freq, actual_freq)

        return min(score, 1.0)

    def _check_common_words_after_conversion(
        self, text: str, conversion_type: str
    ) -> float:
        """Check for common words after applying layout conversion."""
        if conversion_type == "ru_to_en":
            mapping = RU_TO_EN_MAPPING
            common_words = COMMON_ENGLISH_WORDS
        else:  # en_to_ru
            mapping = EN_TO_RU_MAPPING
            common_words = COMMON_RUSSIAN_WORDS

        # Convert text using mapping
        converted_text = self._convert_text(text, mapping)

        # Extract words and check against common words
        words = re.findall(r"\b\w+\b", converted_text.lower())
        if not words:
            return 0.0

        common_word_count = sum(1 for word in words if word in common_words)
        return common_word_count / len(words)

    def _check_current_words(self, text: str, language: str) -> float:
        """Check for common words in the current text without conversion."""
        common_words = (
            COMMON_RUSSIAN_WORDS if language == "ru" else COMMON_ENGLISH_WORDS
        )

        # Extract words from current text
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return 0.0

        common_word_count = sum(1 for word in words if word in common_words)
        return common_word_count / len(words)

    def _convert_text(self, text: str, mapping: Dict[str, str]) -> str:
        """Convert text using character mapping."""
        result = []
        for char in text:
            result.append(mapping.get(char, char))
        return "".join(result)
