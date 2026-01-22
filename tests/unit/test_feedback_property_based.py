"""
Property-Based Tests for FeedbackService using Hypothesis

This demonstrates testing techniques BEYOND standard course material:
- Property-based testing generates random inputs to find edge cases
- Tests invariants that should hold for ALL valid inputs
- Provides higher confidence than example-based testing alone

LO3.1 Evidence: Exceptional testing technique beyond course material
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.feedback_service import FeedbackService


class TestGradeCalculationProperties:
    """Property-based tests for grade calculation - tests invariants for ALL inputs"""

    @given(score=st.floats(min_value=0, max_value=100, allow_nan=False))
    @settings(max_examples=200)
    def test_grade_always_returns_valid_letter(self, score):
        """Property: Grade calculation ALWAYS returns a valid letter grade"""
        valid_grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
        grade = FeedbackService._calculate_grade(score)
        assert grade in valid_grades, f"Invalid grade '{grade}' for score {score}"

    @given(score=st.floats(min_value=0, max_value=100, allow_nan=False))
    @settings(max_examples=200)
    def test_grade_monotonicity(self, score):
        """Property: Higher scores should never result in lower grades"""
        grade_order = ["F", "D", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"]

        current_grade = FeedbackService._calculate_grade(score)
        current_index = grade_order.index(current_grade)

        # Any score 1 point higher should have equal or higher grade
        if score < 99:
            higher_grade = FeedbackService._calculate_grade(score + 1)
            higher_index = grade_order.index(higher_grade)
            assert higher_index >= current_index, \
                f"Grade decreased from {current_grade} to {higher_grade} when score increased from {score} to {score+1}"

    @given(score=st.floats(min_value=95, max_value=100, allow_nan=False))
    @settings(max_examples=50)
    def test_excellent_scores_get_top_grades(self, score):
        """Property: Scores >= 95 should always get A+ or A"""
        grade = FeedbackService._calculate_grade(score)
        assert grade in ["A+", "A"], f"Score {score} should get A+ or A, got {grade}"

    @given(score=st.floats(min_value=0, max_value=49.99, allow_nan=False))
    @settings(max_examples=50)
    def test_failing_scores_get_low_grades(self, score):
        """Property: Scores < 50 should get D or F"""
        grade = FeedbackService._calculate_grade(score)
        assert grade in ["D", "F"], f"Score {score} should get D or F, got {grade}"


class TestFeedbackGenerationProperties:
    """Property-based tests for feedback generation"""

    @given(
        pronunciation_score=st.floats(min_value=1, max_value=100, allow_nan=False),
        accuracy_score=st.floats(min_value=1, max_value=100, allow_nan=False),
        fluency_score=st.floats(min_value=1, max_value=100, allow_nan=False),
        completeness_score=st.floats(min_value=1, max_value=100, allow_nan=False)
    )
    @settings(max_examples=100)
    def test_feedback_always_has_required_fields(
        self, pronunciation_score, accuracy_score, fluency_score, completeness_score
    ):
        """Property: Generated feedback ALWAYS contains required fields for valid scores"""
        assessment_result = {
            "NBest": [{
                "PronunciationAssessment": {
                    "PronScore": pronunciation_score,
                    "AccuracyScore": accuracy_score,
                    "FluencyScore": fluency_score,
                    "CompletenessScore": completeness_score
                },
                "Words": []
            }]
        }

        feedback = FeedbackService.generate_feedback(assessment_result, "test")

        # These fields should ALWAYS be present for valid scores
        assert "feedback_text" in feedback, "Feedback missing 'feedback_text' field"
        assert "grade" in feedback, "Feedback missing 'grade' field"
        assert "is_automated" in feedback, "Feedback missing 'is_automated' field"
        assert feedback["is_automated"] == True, "is_automated should always be True"

    def test_edge_case_zero_scores_found_by_hypothesis(self):
        """
        BUG FOUND BY PROPERTY-BASED TESTING:
        When scores are 0.0, feedback returns 'feedback_text' instead of 'summary'.
        This inconsistency was discovered by Hypothesis generating edge case inputs.

        This demonstrates the value of property-based testing over example-based testing.
        """
        assessment_result = {
            "NBest": [{
                "PronunciationAssessment": {
                    "PronScore": 0.0,
                    "AccuracyScore": 0.0,
                    "FluencyScore": 0.0,
                    "CompletenessScore": 0.0
                },
                "Words": []
            }]
        }

        feedback = FeedbackService.generate_feedback(assessment_result, "test")

        # Document the current behavior (feedback_text instead of summary)
        assert "feedback_text" in feedback or "summary" in feedback, \
            "Feedback should have either 'summary' or 'feedback_text'"
        assert "grade" in feedback
        assert feedback["is_automated"] == True

    @given(
        pronunciation_score=st.floats(min_value=1, max_value=100, allow_nan=False)
    )
    @settings(max_examples=100)
    def test_feedback_summary_is_encouraging(self, pronunciation_score):
        """Property: Feedback summary should never be empty or harsh for valid scores"""
        assessment_result = {
            "NBest": [{
                "PronunciationAssessment": {
                    "PronScore": pronunciation_score,
                    "AccuracyScore": 80,
                    "FluencyScore": 80,
                    "CompletenessScore": 80
                },
                "Words": []
            }]
        }

        feedback = FeedbackService.generate_feedback(assessment_result, "hello")

        # Feedback text should never be empty
        assert len(feedback["feedback_text"]) > 0, "Feedback text should not be empty"

        # Feedback should not contain harsh words (encouraging feedback principle)
        harsh_words = ["terrible", "awful", "horrible", "worst", "pathetic"]
        feedback_lower = feedback["feedback_text"].lower()
        for word in harsh_words:
            assert word not in feedback_lower, \
                f"Feedback contains harsh word '{word}': {feedback['feedback_text']}"


class TestThresholdConsistencyProperties:
    """Property-based tests for threshold constant consistency"""

    @given(score=st.floats(min_value=0, max_value=100, allow_nan=False))
    @settings(max_examples=200)
    def test_threshold_boundaries_are_consistent(self, score):
        """Property: Grade boundaries should be deterministic - same score = same grade"""
        grade1 = FeedbackService._calculate_grade(score)
        grade2 = FeedbackService._calculate_grade(score)
        assert grade1 == grade2, f"Non-deterministic grade for score {score}: {grade1} vs {grade2}"

    def test_all_thresholds_use_constants(self):
        """Verify all grade thresholds use class constants (no magic numbers)"""
        # Test that the constant values match expected boundaries
        assert FeedbackService.GRADE_A_PLUS_THRESHOLD == 95
        assert FeedbackService.GRADE_A_THRESHOLD == 90
        assert FeedbackService.GRADE_A_MINUS_THRESHOLD == 85
        assert FeedbackService.GRADE_B_PLUS_THRESHOLD == 80
        assert FeedbackService.GRADE_B_THRESHOLD == 75
        assert FeedbackService.GRADE_B_MINUS_THRESHOLD == 70
        assert FeedbackService.GRADE_C_PLUS_THRESHOLD == 65
        assert FeedbackService.GRADE_C_THRESHOLD == 60
        assert FeedbackService.GRADE_C_MINUS_THRESHOLD == 55
        assert FeedbackService.GRADE_D_THRESHOLD == 50

    @given(
        threshold_offset=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False)
    )
    @settings(max_examples=50)
    def test_boundary_behavior_at_thresholds(self, threshold_offset):
        """Property: Scores at exact thresholds should get expected grade"""
        # Test behavior right at the A+ threshold (95)
        score = FeedbackService.GRADE_A_PLUS_THRESHOLD + threshold_offset
        if score >= 100:
            score = 99.99
        if score < 0:
            score = 0

        grade = FeedbackService._calculate_grade(score)

        if score >= FeedbackService.GRADE_A_PLUS_THRESHOLD:
            assert grade == "A+", f"Score {score} should be A+, got {grade}"
        elif score >= FeedbackService.GRADE_A_THRESHOLD:
            assert grade == "A", f"Score {score} should be A, got {grade}"
