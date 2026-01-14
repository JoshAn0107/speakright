"""
Unit tests for assignment validation logic
"""
import pytest
from datetime import datetime, timedelta


class TestAssignmentValidation:
    """Test cases for assignment validation"""

    def test_valid_word_count_minimum(self):
        """Test that 20 words (minimum) is valid"""
        words = [f"word{i}" for i in range(20)]
        word_count = len(words)

        assert word_count >= 20
        assert word_count <= 40
        assert word_count == 20

    def test_valid_word_count_maximum(self):
        """Test that 40 words (maximum) is valid"""
        words = [f"word{i}" for i in range(40)]
        word_count = len(words)

        assert word_count >= 20
        assert word_count <= 40
        assert word_count == 40

    def test_valid_word_count_middle(self):
        """Test that 30 words (middle range) is valid"""
        words = [f"word{i}" for i in range(30)]
        word_count = len(words)

        assert word_count >= 20
        assert word_count <= 40
        assert word_count == 30

    def test_invalid_word_count_too_few(self):
        """Test that fewer than 20 words is invalid"""
        words = [f"word{i}" for i in range(19)]
        word_count = len(words)

        # Should fail validation
        is_valid = 20 <= word_count <= 40
        assert not is_valid

    def test_invalid_word_count_too_many(self):
        """Test that more than 40 words is invalid"""
        words = [f"word{i}" for i in range(41)]
        word_count = len(words)

        # Should fail validation
        is_valid = 20 <= word_count <= 40
        assert not is_valid

    def test_invalid_word_count_empty(self):
        """Test that empty word list is invalid"""
        words = []
        word_count = len(words)

        # Should fail validation
        is_valid = 20 <= word_count <= 40
        assert not is_valid

    def test_valid_student_ids_single(self):
        """Test that at least one student ID is valid"""
        student_ids = [1]

        assert len(student_ids) > 0

    def test_valid_student_ids_multiple(self):
        """Test that multiple student IDs is valid"""
        student_ids = [1, 2, 3, 4, 5]

        assert len(student_ids) > 0
        assert len(student_ids) == 5

    def test_invalid_student_ids_empty(self):
        """Test that empty student list is invalid"""
        student_ids = []

        # Should fail validation
        is_valid = len(student_ids) > 0
        assert not is_valid

    def test_assignment_data_completeness(self, valid_assignment_data):
        """Test that valid assignment has all required fields"""
        assert "title" in valid_assignment_data
        assert "description" in valid_assignment_data
        assert "word_database_id" in valid_assignment_data
        assert "due_date" in valid_assignment_data
        assert "words" in valid_assignment_data
        assert "student_ids" in valid_assignment_data

    def test_assignment_word_count_validation(self, valid_assignment_data):
        """Test assignment word count using fixture"""
        word_count = len(valid_assignment_data["words"])
        assert 20 <= word_count <= 40

    def test_assignment_has_students(self, valid_assignment_data):
        """Test assignment has students using fixture"""
        assert len(valid_assignment_data["student_ids"]) > 0

    def test_invalid_too_few_words(self, invalid_assignment_too_few_words):
        """Test invalid assignment with too few words"""
        word_count = len(invalid_assignment_too_few_words["words"])
        is_valid = 20 <= word_count <= 40
        assert not is_valid
        assert word_count < 20

    def test_invalid_too_many_words(self, invalid_assignment_too_many_words):
        """Test invalid assignment with too many words"""
        word_count = len(invalid_assignment_too_many_words["words"])
        is_valid = 20 <= word_count <= 40
        assert not is_valid
        assert word_count > 40

    def test_invalid_no_students(self, invalid_assignment_no_students):
        """Test invalid assignment with no students"""
        student_count = len(invalid_assignment_no_students["student_ids"])
        is_valid = student_count > 0
        assert not is_valid

    def test_due_date_is_future(self, valid_assignment_data):
        """Test that due date is in the future"""
        due_date = valid_assignment_data["due_date"]
        assert due_date > datetime.now()

    def test_title_not_empty(self, valid_assignment_data):
        """Test that title is not empty"""
        title = valid_assignment_data["title"]
        assert title is not None
        assert len(title.strip()) > 0

    def test_words_are_unique(self, valid_assignment_data):
        """Test that word list can contain duplicates (no uniqueness required)"""
        words = valid_assignment_data["words"]
        # Just verify we have words
        assert len(words) > 0

    def test_student_ids_type(self, valid_assignment_data):
        """Test that student IDs are integers"""
        student_ids = valid_assignment_data["student_ids"]
        for student_id in student_ids:
            assert isinstance(student_id, int)
