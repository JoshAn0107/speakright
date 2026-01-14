"""
Unit tests for FeedbackService
Covers L01 Requirements: 3.a, 3.b, 3.c, 3.i
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.feedback_service import FeedbackService


class TestCalculateGrade:
    """
    L01 Requirement 3.a: The _calculate_grade function should correctly
    convert numerical scores to letter grades

    Testing approach: Functional category-partition testing
    Partitions: A+ (95-100), A (90-94), A- (85-89), B+ (80-84), B (75-79),
                B- (70-74), C+ (65-69), C (60-64), C- (55-59), D (50-54), F (<50)
    """

    def test_grade_a_plus_lower_boundary(self):
        """Test A+ grade at lower boundary (95)"""
        assert FeedbackService._calculate_grade(95) == "A+"

    def test_grade_a_plus_upper_boundary(self):
        """Test A+ grade at upper boundary (100)"""
        assert FeedbackService._calculate_grade(100) == "A+"

    def test_grade_a_plus_mid_range(self):
        """Test A+ grade in middle of range"""
        assert FeedbackService._calculate_grade(97) == "A+"

    def test_grade_a_lower_boundary(self):
        """Test A grade at lower boundary (90)"""
        assert FeedbackService._calculate_grade(90) == "A"

    def test_grade_a_upper_boundary(self):
        """Test A grade just below A+ threshold"""
        assert FeedbackService._calculate_grade(94.9) == "A"

    def test_grade_a_mid_range(self):
        """Test A grade in middle of range"""
        assert FeedbackService._calculate_grade(92) == "A"

    def test_grade_a_minus_lower_boundary(self):
        """Test A- grade at lower boundary (85)"""
        assert FeedbackService._calculate_grade(85) == "A-"

    def test_grade_a_minus_upper_boundary(self):
        """Test A- grade just below A threshold"""
        assert FeedbackService._calculate_grade(89.9) == "A-"

    def test_grade_b_plus_lower_boundary(self):
        """Test B+ grade at lower boundary (80)"""
        assert FeedbackService._calculate_grade(80) == "B+"

    def test_grade_b_plus_upper_boundary(self):
        """Test B+ grade at upper boundary"""
        assert FeedbackService._calculate_grade(84) == "B+"

    def test_grade_b_lower_boundary(self):
        """Test B grade at lower boundary (75)"""
        assert FeedbackService._calculate_grade(75) == "B"

    def test_grade_b_upper_boundary(self):
        """Test B grade at upper boundary"""
        assert FeedbackService._calculate_grade(79) == "B"

    def test_grade_b_minus(self):
        """Test B- grade (70-74)"""
        assert FeedbackService._calculate_grade(70) == "B-"
        assert FeedbackService._calculate_grade(72) == "B-"

    def test_grade_c_plus(self):
        """Test C+ grade (65-69)"""
        assert FeedbackService._calculate_grade(65) == "C+"
        assert FeedbackService._calculate_grade(67) == "C+"

    def test_grade_c(self):
        """Test C grade (60-64)"""
        assert FeedbackService._calculate_grade(60) == "C"
        assert FeedbackService._calculate_grade(62) == "C"

    def test_grade_c_minus(self):
        """Test C- grade (55-59)"""
        assert FeedbackService._calculate_grade(55) == "C-"
        assert FeedbackService._calculate_grade(57) == "C-"

    def test_grade_d_lower_boundary(self):
        """Test D grade at lower boundary (50)"""
        assert FeedbackService._calculate_grade(50) == "D"

    def test_grade_d_upper_boundary(self):
        """Test D grade at upper boundary"""
        assert FeedbackService._calculate_grade(54) == "D"

    def test_grade_f_just_below_d(self):
        """Test F grade just below D threshold"""
        assert FeedbackService._calculate_grade(49.9) == "F"

    def test_grade_f_very_low(self):
        """Test F grade with very low score"""
        assert FeedbackService._calculate_grade(30) == "F"
        assert FeedbackService._calculate_grade(0) == "F"

    def test_grade_boundary_transitions(self):
        """Test exact boundary transitions between grades"""
        # Test all major boundaries
        assert FeedbackService._calculate_grade(94.99) == "A"
        assert FeedbackService._calculate_grade(95.0) == "A+"
        assert FeedbackService._calculate_grade(89.99) == "A-"
        assert FeedbackService._calculate_grade(90.0) == "A"
        assert FeedbackService._calculate_grade(49.99) == "F"
        assert FeedbackService._calculate_grade(50.0) == "D"


class TestAnalyzePhonemes:
    """
    L01 Requirement 3.b: The _analyze_phonemes function should correctly
    identify problem phonemes with accuracy scores below 60

    Testing approach: Functional category-partition testing
    Partitions: No phoneme data, all good scores (≥60), some poor scores (<60),
                many poor scores (limit to 3), missing accuracy scores
    """

    def test_no_phoneme_data_no_words(self):
        """Test with assessment result containing no words"""
        assessment_result = {"words": []}
        feedback = FeedbackService._analyze_phonemes(assessment_result)
        assert feedback is None

    def test_no_phoneme_data_missing_words_key(self):
        """Test with assessment result missing 'words' key"""
        assessment_result = {"pronunciation_score": 85}
        feedback = FeedbackService._analyze_phonemes(assessment_result)
        assert feedback is None

    def test_no_phoneme_data_in_words(self):
        """Test with words but no phoneme data"""
        assessment_result = {
            "words": [
                {"word": "test"}
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)
        assert feedback is None

    def test_all_good_phoneme_scores(self):
        """Test with all phoneme scores above threshold (≥60)"""
        assessment_result = {
            "words": [
                {
                    "word": "beautiful",
                    "phonemes": [
                        {"phoneme": "b", "accuracy_score": 85},
                        {"phoneme": "juː", "accuracy_score": 90},
                        {"phoneme": "t", "accuracy_score": 75},
                        {"phoneme": "ɪ", "accuracy_score": 80},
                        {"phoneme": "f", "accuracy_score": 95},
                        {"phoneme": "əl", "accuracy_score": 88}
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)
        assert feedback is None

    def test_some_poor_phoneme_scores(self):
        """Test with some phonemes below threshold (<60)"""
        assessment_result = {
            "words": [
                {
                    "word": "comfortable",
                    "phonemes": [
                        {"phoneme": "k", "accuracy_score": 85},
                        {"phoneme": "ʌ", "accuracy_score": 55},  # Poor
                        {"phoneme": "m", "accuracy_score": 75},
                        {"phoneme": "f", "accuracy_score": 58},  # Poor
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is not None
        assert "special attention" in feedback.lower() or "pay" in feedback.lower()
        assert "/ʌ/" in feedback
        assert "/f/" in feedback

    def test_many_poor_phonemes_limits_to_three(self):
        """Test that function limits problem phonemes to first 3"""
        assessment_result = {
            "words": [
                {
                    "word": "pronunciation",
                    "phonemes": [
                        {"phoneme": "p", "accuracy_score": 50},  # Poor 1
                        {"phoneme": "r", "accuracy_score": 45},  # Poor 2
                        {"phoneme": "ə", "accuracy_score": 55},  # Poor 3
                        {"phoneme": "n", "accuracy_score": 48},  # Poor 4
                        {"phoneme": "ʌ", "accuracy_score": 52},  # Poor 5
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is not None
        # Should mention only first 3 problem phonemes
        phoneme_count = feedback.count("/")
        assert phoneme_count == 6  # 3 phonemes * 2 (opening and closing /)

    def test_phoneme_at_exact_threshold(self):
        """Test phoneme at exact threshold of 60"""
        assessment_result = {
            "words": [
                {
                    "word": "test",
                    "phonemes": [
                        {"phoneme": "t", "accuracy_score": 60},  # Exactly at threshold
                        {"phoneme": "ɛ", "accuracy_score": 59},  # Just below
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)

        # 60 should not be included (threshold is <60)
        assert feedback is not None
        assert "/t/" not in feedback
        assert "/ɛ/" in feedback

    def test_missing_phoneme_accuracy_scores(self):
        """Test handling of phonemes with missing accuracy scores"""
        assessment_result = {
            "words": [
                {
                    "word": "test",
                    "phonemes": [
                        {"phoneme": "t"},  # Missing accuracy_score
                        {"phoneme": "ɛ", "accuracy_score": 55},
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)

        # Should handle missing scores gracefully (default to 100)
        assert feedback is not None
        assert "/ɛ/" in feedback

    def test_empty_phoneme_text(self):
        """Test handling of empty phoneme text"""
        assessment_result = {
            "words": [
                {
                    "word": "test",
                    "phonemes": [
                        {"phoneme": "", "accuracy_score": 50},
                        {"phoneme": "t", "accuracy_score": 55},
                    ]
                }
            ]
        }
        feedback = FeedbackService._analyze_phonemes(assessment_result)

        # Should skip empty phoneme text
        assert feedback is not None
        assert "/t/" in feedback


class TestEnhanceFeedback:
    """
    L01 Requirement 3.c: The enhance_feedback_with_teacher_notes function
    should correctly combine automated feedback with teacher notes

    Testing approach: Functional category-partition testing
    Partitions: Teacher notes provided, empty notes, whitespace-only notes,
                very long notes
    """

    def test_with_teacher_notes_provided(self):
        """Test combining automated feedback with valid teacher notes"""
        automated = "Good pronunciation!"
        teacher_notes = "Focus on the 'th' sound."

        result = FeedbackService.enhance_feedback_with_teacher_notes(
            automated, teacher_notes
        )

        assert "Good pronunciation!" in result
        assert "Focus on the 'th' sound." in result
        assert "Teacher's Note" in result

    def test_with_empty_teacher_notes(self):
        """Test that empty teacher notes return original feedback"""
        automated = "Good pronunciation!"
        teacher_notes = ""

        result = FeedbackService.enhance_feedback_with_teacher_notes(
            automated, teacher_notes
        )

        assert result == automated

    def test_with_whitespace_only_teacher_notes(self):
        """Test that whitespace-only notes return original feedback"""
        automated = "Good pronunciation!"
        teacher_notes = "   \t\n  "

        result = FeedbackService.enhance_feedback_with_teacher_notes(
            automated, teacher_notes
        )

        assert result == automated

    def test_with_multiline_teacher_notes(self):
        """Test handling of multiline teacher notes"""
        automated = "Good pronunciation!"
        teacher_notes = "Focus on:\n1. The 'th' sound\n2. Word stress"

        result = FeedbackService.enhance_feedback_with_teacher_notes(
            automated, teacher_notes
        )

        assert "Good pronunciation!" in result
        assert "Focus on:" in result
        assert "The 'th' sound" in result
        assert "Teacher's Note" in result

    def test_with_very_long_teacher_notes(self):
        """Test handling of very long teacher notes"""
        automated = "Good pronunciation!"
        teacher_notes = "A" * 500  # 500 character note

        result = FeedbackService.enhance_feedback_with_teacher_notes(
            automated, teacher_notes
        )

        assert "Good pronunciation!" in result
        assert teacher_notes in result
        assert len(result) > 500


class TestGenerateFeedback:
    """
    L01 Requirement 3.i: The generate_feedback function should include
    appropriate feedback components based on score ranges

    Testing approach: Functional category-partition testing
    Partitions: Excellent (90-100), very good (80-89), good (70-79),
                fair (60-69), needs improvement (50-59), poor (<50),
                missing assessment data
    """

    def test_excellent_pronunciation_90_100(self, sample_pronunciation_result_excellent):
        """Test feedback for excellent pronunciation (90-100)"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_excellent, "beautiful"
        )

        assert result["grade"] == "A+"
        assert result["is_automated"] is True
        assert "beautiful" in result["feedback_text"]
        assert ("Excellent" in result["feedback_text"] or
                "excellent" in result["feedback_text"].lower())

    def test_very_good_pronunciation_80_89(self):
        """Test feedback for very good pronunciation (80-89)"""
        assessment = {
            "pronunciation_score": 85,
            "accuracy_score": 84,
            "fluency_score": 86,
            "completeness_score": 85
        }
        result = FeedbackService.generate_feedback(assessment, "wonderful")

        assert result["grade"] == "A-"
        assert result["is_automated"] is True
        assert "wonderful" in result["feedback_text"]

    def test_good_pronunciation_70_79(self):
        """Test feedback for good pronunciation (70-79)"""
        assessment = {
            "pronunciation_score": 75,
            "accuracy_score": 73,
            "fluency_score": 77,
            "completeness_score": 76
        }
        result = FeedbackService.generate_feedback(assessment, "interesting")

        assert result["grade"] == "B"
        assert result["is_automated"] is True
        assert "interesting" in result["feedback_text"]

    def test_fair_pronunciation_60_69(self, sample_pronunciation_result_needs_improvement):
        """Test feedback for fair pronunciation (60-69)"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_needs_improvement, "comfortable"
        )

        assert result["grade"] in ["C+", "C", "C-"]
        assert result["is_automated"] is True
        assert "comfortable" in result["feedback_text"]

    def test_needs_improvement_50_59(self):
        """Test feedback for pronunciation that needs improvement (50-59)"""
        assessment = {
            "pronunciation_score": 55,
            "accuracy_score": 52,
            "fluency_score": 58,
            "completeness_score": 56
        }
        result = FeedbackService.generate_feedback(assessment, "difficult")

        assert result["grade"] == "C-"
        assert result["is_automated"] is True
        assert "difficult" in result["feedback_text"]

    def test_poor_pronunciation_below_50(self, sample_pronunciation_result_poor):
        """Test feedback for poor pronunciation (<50)"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_poor, "pronunciation"
        )

        assert result["grade"] == "F"
        assert result["is_automated"] is True
        assert "pronunciation" in result["feedback_text"]

    def test_missing_assessment_data_empty_dict(self):
        """Test feedback with empty assessment result"""
        result = FeedbackService.generate_feedback({}, "test")

        assert result["grade"] == "N/A"
        assert result["is_automated"] is True
        assert "Unable to assess" in result["feedback_text"]

    def test_missing_assessment_data_no_score(self):
        """Test feedback with missing pronunciation score"""
        assessment = {
            "accuracy_score": 80,
            "fluency_score": 75
        }
        result = FeedbackService.generate_feedback(assessment, "test")

        assert result["grade"] == "N/A"
        assert result["is_automated"] is True

    def test_feedback_includes_strengths_for_high_scores(self):
        """Test that high scores include strength mentions"""
        assessment = {
            "pronunciation_score": 92,
            "accuracy_score": 90,
            "fluency_score": 94,
            "completeness_score": 91
        }
        result = FeedbackService.generate_feedback(assessment, "test")

        assert ("Strengths" in result["feedback_text"] or
                "accurate" in result["feedback_text"].lower() or
                "excellent" in result["feedback_text"].lower())

    def test_feedback_includes_areas_to_improve_for_low_scores(self):
        """Test that low scores include improvement suggestions"""
        assessment = {
            "pronunciation_score": 65,
            "accuracy_score": 62,
            "fluency_score": 60,
            "completeness_score": 70
        }
        result = FeedbackService.generate_feedback(assessment, "test")

        assert ("Focus" in result["feedback_text"] or
                "improve" in result["feedback_text"].lower() or
                "practice" in result["feedback_text"].lower())

    def test_feedback_includes_tips_for_different_score_ranges(self):
        """Test that appropriate tips are included based on score range"""
        # Below 70 - should include basic tips
        low_assessment = {
            "pronunciation_score": 65,
            "accuracy_score": 63,
            "fluency_score": 67,
            "completeness_score": 66
        }
        low_result = FeedbackService.generate_feedback(low_assessment, "test")
        assert "Tip" in low_result["feedback_text"] or "💡" in low_result["feedback_text"]

        # 70-85 - should include intermediate tips
        mid_assessment = {
            "pronunciation_score": 78,
            "accuracy_score": 76,
            "fluency_score": 80,
            "completeness_score": 79
        }
        mid_result = FeedbackService.generate_feedback(mid_assessment, "test")
        assert "Tip" in mid_result["feedback_text"] or "💡" in mid_result["feedback_text"]

        # Above 85 - should include encouragement
        high_assessment = {
            "pronunciation_score": 90,
            "accuracy_score": 89,
            "fluency_score": 92,
            "completeness_score": 91
        }
        high_result = FeedbackService.generate_feedback(high_assessment, "test")
        assert ("excellent" in high_result["feedback_text"].lower() or
                "Keep up" in high_result["feedback_text"])
