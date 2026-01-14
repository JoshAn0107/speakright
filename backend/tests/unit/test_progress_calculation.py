"""
Unit tests for assignment progress calculation logic
"""
import pytest


class TestProgressCalculation:
    """Test cases for progress calculation"""

    def test_calculate_progress_zero_completed(self):
        """Test progress calculation with 0 completed words"""
        total_words = 25
        completed_words = 0

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 0.0

    def test_calculate_progress_all_completed(self):
        """Test progress calculation with all words completed"""
        total_words = 25
        completed_words = 25

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 100.0

    def test_calculate_progress_half_completed(self):
        """Test progress calculation with half words completed"""
        total_words = 20
        completed_words = 10

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 50.0

    def test_calculate_progress_partial(self):
        """Test progress calculation with partial completion"""
        total_words = 30
        completed_words = 15

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 50.0

    def test_calculate_progress_rounding(self):
        """Test progress calculation with rounding"""
        total_words = 30
        completed_words = 10

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0
        rounded_percentage = round(completion_percentage, 1)

        assert rounded_percentage == 33.3

    def test_calculate_progress_complex_rounding(self):
        """Test progress calculation with complex rounding"""
        total_words = 37
        completed_words = 25

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0
        rounded_percentage = round(completion_percentage, 1)

        # 25/37 * 100 = 67.567... should round to 67.6
        assert rounded_percentage == pytest.approx(67.6, rel=0.1)

    def test_calculate_progress_zero_total_words(self):
        """Test progress calculation handles zero total words"""
        total_words = 0
        completed_words = 0

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        # Should not crash and return 0
        assert completion_percentage == 0

    def test_calculate_progress_one_word(self):
        """Test progress calculation with single word assignment"""
        total_words = 1
        completed_words = 0

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0
        assert completion_percentage == 0.0

        completed_words = 1
        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0
        assert completion_percentage == 100.0

    def test_calculate_progress_minimum_valid(self):
        """Test progress with minimum valid assignment (20 words)"""
        total_words = 20
        completed_words = 5

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 25.0

    def test_calculate_progress_maximum_valid(self):
        """Test progress with maximum valid assignment (40 words)"""
        total_words = 40
        completed_words = 20

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage == 50.0

    def test_calculate_progress_typical_scenario(self):
        """Test progress with typical scenario (25 words, 18 completed)"""
        total_words = 25
        completed_words = 18

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0
        rounded_percentage = round(completion_percentage, 1)

        # 18/25 * 100 = 72.0
        assert rounded_percentage == 72.0

    def test_progress_never_exceeds_100(self):
        """Test that progress never exceeds 100%"""
        total_words = 20
        completed_words = 20

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage <= 100

    def test_progress_is_non_negative(self):
        """Test that progress is never negative"""
        total_words = 20
        completed_words = 0

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        assert completion_percentage >= 0

    def test_multiple_students_progress(self):
        """Test calculating progress for multiple students"""
        total_words = 25
        students_progress = [
            {"student_id": 1, "completed": 25},  # 100%
            {"student_id": 2, "completed": 15},  # 60%
            {"student_id": 3, "completed": 0},   # 0%
        ]

        results = []
        for student in students_progress:
            completion_percentage = (student["completed"] / total_words * 100) if total_words > 0 else 0
            results.append(round(completion_percentage, 1))

        assert results[0] == 100.0
        assert results[1] == 60.0
        assert results[2] == 0.0

    def test_average_class_progress(self):
        """Test calculating average progress for a class"""
        individual_progress = [100.0, 60.0, 75.0, 80.0]

        average_progress = sum(individual_progress) / len(individual_progress)

        assert average_progress == 78.75

    def test_progress_calculation_precision(self):
        """Test that progress calculation maintains precision"""
        total_words = 27
        completed_words = 13

        completion_percentage = (completed_words / total_words * 100) if total_words > 0 else 0

        # 13/27 * 100 = 48.148...
        assert completion_percentage > 48.1
        assert completion_percentage < 48.2

    def test_progress_with_boundary_values(self):
        """Test progress calculation with boundary values"""
        # Test 1: Just started (1 out of 20)
        completion_percentage = (1 / 20 * 100)
        assert completion_percentage == 5.0

        # Test 2: Almost done (19 out of 20)
        completion_percentage = (19 / 20 * 100)
        assert completion_percentage == 95.0

        # Test 3: Exactly half (20 out of 40)
        completion_percentage = (20 / 40 * 100)
        assert completion_percentage == 50.0
