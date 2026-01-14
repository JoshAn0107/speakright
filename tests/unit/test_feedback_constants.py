"""
Unit tests for FeedbackService constants
Tests that threshold constants are properly defined and accessible
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.feedback_service import FeedbackService


class TestFeedbackConstants:
    """Test that all threshold constants are properly defined"""

    def test_performance_thresholds_exist(self):
        """Verify all performance threshold constants are defined"""
        assert hasattr(FeedbackService, 'EXCELLENT_THRESHOLD')
        assert hasattr(FeedbackService, 'GREAT_THRESHOLD')
        assert hasattr(FeedbackService, 'GOOD_THRESHOLD')
        assert hasattr(FeedbackService, 'OKAY_THRESHOLD')

    def test_component_thresholds_exist(self):
        """Verify all component score threshold constants are defined"""
        assert hasattr(FeedbackService, 'ACCURACY_LOW_THRESHOLD')
        assert hasattr(FeedbackService, 'ACCURACY_HIGH_THRESHOLD')
        assert hasattr(FeedbackService, 'FLUENCY_LOW_THRESHOLD')
        assert hasattr(FeedbackService, 'FLUENCY_HIGH_THRESHOLD')
        assert hasattr(FeedbackService, 'COMPLETENESS_LOW_THRESHOLD')
        assert hasattr(FeedbackService, 'COMPLETENESS_HIGH_THRESHOLD')

    def test_phoneme_thresholds_exist(self):
        """Verify phoneme analysis threshold constants are defined"""
        assert hasattr(FeedbackService, 'PHONEME_PROBLEM_THRESHOLD')
        assert hasattr(FeedbackService, 'MAX_PHONEME_FEEDBACK_COUNT')

    def test_threshold_values_are_logical(self):
        """Verify threshold values follow logical ordering"""
        # Performance thresholds should be descending
        assert FeedbackService.EXCELLENT_THRESHOLD > FeedbackService.GREAT_THRESHOLD
        assert FeedbackService.GREAT_THRESHOLD > FeedbackService.GOOD_THRESHOLD
        assert FeedbackService.GOOD_THRESHOLD > FeedbackService.OKAY_THRESHOLD

        # Component thresholds: high should be > low
        assert FeedbackService.ACCURACY_HIGH_THRESHOLD > FeedbackService.ACCURACY_LOW_THRESHOLD
        assert FeedbackService.FLUENCY_HIGH_THRESHOLD > FeedbackService.FLUENCY_LOW_THRESHOLD
        assert FeedbackService.COMPLETENESS_HIGH_THRESHOLD > FeedbackService.COMPLETENESS_LOW_THRESHOLD

    def test_threshold_consistency_with_grade_boundaries(self):
        """
        Test that performance thresholds align with grade calculation boundaries
        """
        # EXCELLENT_THRESHOLD (90) is the "A" boundary, not "A+" (which is 95)
        assert FeedbackService._calculate_grade(FeedbackService.EXCELLENT_THRESHOLD) == "A"

        # GREAT_THRESHOLD (80) is the "B+" boundary
        assert FeedbackService._calculate_grade(FeedbackService.GREAT_THRESHOLD) == "B+"

        # GOOD_THRESHOLD (70) is the "B-" boundary
        assert FeedbackService._calculate_grade(FeedbackService.GOOD_THRESHOLD) == "B-"

        # OKAY_THRESHOLD (60) is the "C" boundary
        assert FeedbackService._calculate_grade(FeedbackService.OKAY_THRESHOLD) == "C"

    def test_max_phoneme_count_is_reasonable(self):
        """Verify max phoneme feedback count is reasonable (not too many)"""
        assert FeedbackService.MAX_PHONEME_FEEDBACK_COUNT <= 5
        assert FeedbackService.MAX_PHONEME_FEEDBACK_COUNT >= 1
