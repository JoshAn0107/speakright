"""
Unit tests for feedback service business logic
"""
import pytest
from app.services.feedback_service import FeedbackService


class TestFeedbackService:
    """Test cases for FeedbackService"""

    def test_calculate_grade_a_plus(self):
        """Test grade calculation for A+ (95-100)"""
        grade = FeedbackService._calculate_grade(95)
        assert grade == "A+"

        grade = FeedbackService._calculate_grade(97)
        assert grade == "A+"

        grade = FeedbackService._calculate_grade(100)
        assert grade == "A+"

    def test_calculate_grade_a(self):
        """Test grade calculation for A (90-94)"""
        grade = FeedbackService._calculate_grade(90)
        assert grade == "A"

        grade = FeedbackService._calculate_grade(92)
        assert grade == "A"

        grade = FeedbackService._calculate_grade(94)
        assert grade == "A"

    def test_calculate_grade_a_minus(self):
        """Test grade calculation for A- (85-89)"""
        grade = FeedbackService._calculate_grade(85)
        assert grade == "A-"

        grade = FeedbackService._calculate_grade(87)
        assert grade == "A-"

        grade = FeedbackService._calculate_grade(89)
        assert grade == "A-"

    def test_calculate_grade_b_plus(self):
        """Test grade calculation for B+ (80-84)"""
        grade = FeedbackService._calculate_grade(80)
        assert grade == "B+"

        grade = FeedbackService._calculate_grade(82)
        assert grade == "B+"

    def test_calculate_grade_b(self):
        """Test grade calculation for B (75-79)"""
        grade = FeedbackService._calculate_grade(75)
        assert grade == "B"

        grade = FeedbackService._calculate_grade(77)
        assert grade == "B"

    def test_calculate_grade_c(self):
        """Test grade calculation for C range (60-69)"""
        grade = FeedbackService._calculate_grade(65)
        assert grade == "C+"

        grade = FeedbackService._calculate_grade(60)
        assert grade == "C"

    def test_calculate_grade_d(self):
        """Test grade calculation for D (50-54)"""
        grade = FeedbackService._calculate_grade(50)
        assert grade == "D"

        grade = FeedbackService._calculate_grade(52)
        assert grade == "D"

    def test_calculate_grade_f(self):
        """Test grade calculation for F (below 50)"""
        grade = FeedbackService._calculate_grade(49)
        assert grade == "F"

        grade = FeedbackService._calculate_grade(30)
        assert grade == "F"

        grade = FeedbackService._calculate_grade(0)
        assert grade == "F"

    def test_generate_feedback_excellent(self, sample_pronunciation_result_excellent):
        """Test feedback generation for excellent pronunciation"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_excellent,
            "beautiful"
        )

        assert result["grade"] == "A+"
        assert result["is_automated"] is True
        assert "beautiful" in result["feedback_text"]
        assert "Excellent" in result["feedback_text"] or "excellent" in result["feedback_text"].lower()

    def test_generate_feedback_needs_improvement(self, sample_pronunciation_result_needs_improvement):
        """Test feedback generation for pronunciation that needs improvement"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_needs_improvement,
            "comfortable"
        )

        assert result["grade"] in ["C+", "C", "C-", "D"]
        assert result["is_automated"] is True
        assert "comfortable" in result["feedback_text"]

    def test_generate_feedback_poor(self, sample_pronunciation_result_poor):
        """Test feedback generation for poor pronunciation"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_poor,
            "pronunciation"
        )

        assert result["grade"] == "F"
        assert result["is_automated"] is True
        assert "pronunciation" in result["feedback_text"]

    def test_generate_feedback_empty_result(self):
        """Test feedback generation with empty assessment result"""
        result = FeedbackService.generate_feedback({}, "test")

        assert result["grade"] == "N/A"
        assert result["is_automated"] is True
        assert "Unable to assess" in result["feedback_text"]

    def test_generate_feedback_missing_score(self):
        """Test feedback generation with missing pronunciation score"""
        assessment_result = {
            "accuracy_score": 80,
            "fluency_score": 75
        }

        result = FeedbackService.generate_feedback(assessment_result, "test")

        assert result["grade"] == "N/A"
        assert result["is_automated"] is True

    def test_analyze_phonemes_with_problems(self):
        """Test phoneme analysis identifies problem sounds"""
        assessment_result = {
            "words": [
                {
                    "word": "test",
                    "phonemes": [
                        {"phoneme": "t", "accuracy_score": 85},
                        {"phoneme": "ɛ", "accuracy_score": 55},  # Problem
                        {"phoneme": "s", "accuracy_score": 90},
                        {"phoneme": "t", "accuracy_score": 50}   # Problem
                    ]
                }
            ]
        }

        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is not None
        assert "special attention" in feedback.lower() or "pay" in feedback.lower()

    def test_analyze_phonemes_no_problems(self):
        """Test phoneme analysis with no problems"""
        assessment_result = {
            "words": [
                {
                    "word": "test",
                    "phonemes": [
                        {"phoneme": "t", "accuracy_score": 85},
                        {"phoneme": "ɛ", "accuracy_score": 90},
                        {"phoneme": "s", "accuracy_score": 95},
                        {"phoneme": "t", "accuracy_score": 88}
                    ]
                }
            ]
        }

        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is None

    def test_analyze_phonemes_no_phoneme_data(self):
        """Test phoneme analysis with missing phoneme data"""
        assessment_result = {
            "words": [
                {
                    "word": "test"
                }
            ]
        }

        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is None

    def test_analyze_phonemes_empty_words(self):
        """Test phoneme analysis with empty words list"""
        assessment_result = {
            "words": []
        }

        feedback = FeedbackService._analyze_phonemes(assessment_result)

        assert feedback is None

    def test_enhance_feedback_with_teacher_notes(self):
        """Test enhancing automated feedback with teacher notes"""
        automated_feedback = "Good pronunciation!"
        teacher_notes = "Focus on the 'th' sound."

        enhanced = FeedbackService.enhance_feedback_with_teacher_notes(
            automated_feedback,
            teacher_notes
        )

        assert "Good pronunciation!" in enhanced
        assert "Focus on the 'th' sound." in enhanced
        assert "Teacher's Note" in enhanced

    def test_enhance_feedback_empty_teacher_notes(self):
        """Test enhancing feedback with empty teacher notes"""
        automated_feedback = "Good pronunciation!"
        teacher_notes = ""

        enhanced = FeedbackService.enhance_feedback_with_teacher_notes(
            automated_feedback,
            teacher_notes
        )

        # Should return original feedback unchanged
        assert enhanced == automated_feedback

    def test_enhance_feedback_whitespace_teacher_notes(self):
        """Test enhancing feedback with whitespace-only teacher notes"""
        automated_feedback = "Good pronunciation!"
        teacher_notes = "   "

        enhanced = FeedbackService.enhance_feedback_with_teacher_notes(
            automated_feedback,
            teacher_notes
        )

        # Should return original feedback unchanged
        assert enhanced == automated_feedback

    def test_feedback_includes_grade(self, sample_pronunciation_result_excellent):
        """Test that feedback includes appropriate grade"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_excellent,
            "beautiful"
        )

        # Check grade is present and valid
        assert "grade" in result
        valid_grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F", "N/A"]
        assert result["grade"] in valid_grades

    def test_feedback_identifies_strengths(self, sample_pronunciation_result_excellent):
        """Test that feedback identifies strengths for good performance"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_excellent,
            "beautiful"
        )

        # Should mention strengths
        assert ("Strengths" in result["feedback_text"] or
                "accurate" in result["feedback_text"].lower() or
                "excellent" in result["feedback_text"].lower())

    def test_feedback_identifies_areas_to_improve(self, sample_pronunciation_result_needs_improvement):
        """Test that feedback identifies areas to improve for mediocre performance"""
        result = FeedbackService.generate_feedback(
            sample_pronunciation_result_needs_improvement,
            "comfortable"
        )

        # Should mention areas to improve
        assert ("Focus" in result["feedback_text"] or
                "improve" in result["feedback_text"].lower() or
                "practice" in result["feedback_text"].lower())

    def test_feedback_is_automated_flag(self):
        """Test that all automated feedback is properly flagged"""
        test_result = {
            "pronunciation_score": 75,
            "accuracy_score": 70,
            "fluency_score": 78,
            "completeness_score": 77
        }

        result = FeedbackService.generate_feedback(test_result, "test")

        assert result["is_automated"] is True

    def test_grade_boundaries(self):
        """Test grade boundaries are correct"""
        # Test exact boundary values
        assert FeedbackService._calculate_grade(94.9) == "A"
        assert FeedbackService._calculate_grade(95.0) == "A+"
        assert FeedbackService._calculate_grade(89.9) == "A-"
        assert FeedbackService._calculate_grade(90.0) == "A"
        assert FeedbackService._calculate_grade(49.9) == "F"
        assert FeedbackService._calculate_grade(50.0) == "D"
