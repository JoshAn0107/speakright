"""
Pytest configuration and fixtures for unit tests
"""
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def valid_assignment_data():
    """Fixture providing valid assignment data"""
    return {
        "title": "Test Assignment",
        "description": "Test Description",
        "word_database_id": 1,
        "due_date": datetime.now() + timedelta(days=7),
        "words": [f"word{i}" for i in range(25)],  # 25 words (valid range 20-40)
        "student_ids": [1, 2, 3]
    }


@pytest.fixture
def invalid_assignment_too_few_words():
    """Fixture providing assignment with too few words"""
    return {
        "title": "Test Assignment",
        "description": "Test Description",
        "word_database_id": 1,
        "due_date": datetime.now() + timedelta(days=7),
        "words": [f"word{i}" for i in range(15)],  # Only 15 words (invalid)
        "student_ids": [1, 2, 3]
    }


@pytest.fixture
def invalid_assignment_too_many_words():
    """Fixture providing assignment with too many words"""
    return {
        "title": "Test Assignment",
        "description": "Test Description",
        "word_database_id": 1,
        "due_date": datetime.now() + timedelta(days=7),
        "words": [f"word{i}" for i in range(45)],  # 45 words (invalid)
        "student_ids": [1, 2, 3]
    }


@pytest.fixture
def invalid_assignment_no_students():
    """Fixture providing assignment with no students"""
    return {
        "title": "Test Assignment",
        "description": "Test Description",
        "word_database_id": 1,
        "due_date": datetime.now() + timedelta(days=7),
        "words": [f"word{i}" for i in range(25)],
        "student_ids": []  # No students (invalid)
    }


@pytest.fixture
def sample_pronunciation_result_excellent():
    """Fixture for excellent pronunciation result"""
    return {
        "pronunciation_score": 95,
        "accuracy_score": 94,
        "fluency_score": 96,
        "completeness_score": 95,
        "words": [
            {
                "word": "beautiful",
                "phonemes": [
                    {"phoneme": "b", "accuracy_score": 95},
                    {"phoneme": "juː", "accuracy_score": 93},
                    {"phoneme": "t", "accuracy_score": 94},
                    {"phoneme": "ɪ", "accuracy_score": 96},
                    {"phoneme": "f", "accuracy_score": 92},
                    {"phoneme": "əl", "accuracy_score": 95}
                ]
            }
        ]
    }


@pytest.fixture
def sample_pronunciation_result_needs_improvement():
    """Fixture for pronunciation result that needs improvement"""
    return {
        "pronunciation_score": 65,
        "accuracy_score": 60,
        "fluency_score": 68,
        "completeness_score": 70,
        "words": [
            {
                "word": "comfortable",
                "phonemes": [
                    {"phoneme": "k", "accuracy_score": 85},
                    {"phoneme": "ʌ", "accuracy_score": 55},  # Problem
                    {"phoneme": "m", "accuracy_score": 75},
                    {"phoneme": "f", "accuracy_score": 58},  # Problem
                    {"phoneme": "ə", "accuracy_score": 70},
                    {"phoneme": "t", "accuracy_score": 80},
                    {"phoneme": "ə", "accuracy_score": 72},
                    {"phoneme": "b", "accuracy_score": 78},
                    {"phoneme": "l", "accuracy_score": 50}   # Problem
                ]
            }
        ]
    }


@pytest.fixture
def sample_pronunciation_result_poor():
    """Fixture for poor pronunciation result"""
    return {
        "pronunciation_score": 45,
        "accuracy_score": 40,
        "fluency_score": 48,
        "completeness_score": 47,
        "words": [
            {
                "word": "pronunciation",
                "phonemes": [
                    {"phoneme": "p", "accuracy_score": 50},
                    {"phoneme": "r", "accuracy_score": 35},
                    {"phoneme": "ə", "accuracy_score": 42},
                    {"phoneme": "n", "accuracy_score": 45}
                ]
            }
        ]
    }
