"""
Shared pytest configuration and fixtures for all test levels
"""
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User, UserRole
from app.models.recording import Recording, RecordingStatus
from app.models.word import WordAssignment
from app.models.progress import StudentProgress
from app.core.security import get_password_hash, create_access_token


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function"""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_student(test_db):
    """Create a test student user"""
    student = User(
        username="test_student",
        email="student@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.STUDENT
    )
    test_db.add(student)
    test_db.commit()
    test_db.refresh(student)
    return student


@pytest.fixture
def test_teacher(test_db):
    """Create a test teacher user"""
    teacher = User(
        username="test_teacher",
        email="teacher@test.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.TEACHER
    )
    test_db.add(teacher)
    test_db.commit()
    test_db.refresh(teacher)
    return teacher


@pytest.fixture
def student_token(test_student):
    """Create a JWT token for test student"""
    return create_access_token(data={"sub": str(test_student.id)})


@pytest.fixture
def teacher_token(test_teacher):
    """Create a JWT token for test teacher"""
    return create_access_token(data={"sub": str(test_teacher.id)})


@pytest.fixture
def auth_headers_student(student_token):
    """Create authorization headers for student"""
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def auth_headers_teacher(teacher_token):
    """Create authorization headers for teacher"""
    return {"Authorization": f"Bearer {teacher_token}"}


# ============================================================================
# Recording Fixtures
# ============================================================================

@pytest.fixture
def sample_recording(test_db, test_student):
    """Create a sample recording"""
    recording = Recording(
        student_id=test_student.id,
        word_text="beautiful",
        audio_file_path="/uploads/1/beautiful_20240101_120000.wav",
        automated_scores={
            "pronunciation_score": 85,
            "accuracy_score": 83,
            "fluency_score": 87,
            "completeness_score": 86
        },
        teacher_feedback="Good pronunciation!",
        teacher_grade="B+",
        status=RecordingStatus.REVIEWED
    )
    test_db.add(recording)
    test_db.commit()
    test_db.refresh(recording)
    return recording


@pytest.fixture
def sample_word_assignment(test_db):
    """Create a sample word assignment"""
    word = WordAssignment(
        word_text="beautiful",
        difficulty_level="intermediate",
        topic_tags=["adjectives", "common"],
        times_practiced=5
    )
    test_db.add(word)
    test_db.commit()
    test_db.refresh(word)
    return word


# ============================================================================
# Pronunciation Assessment Fixtures
# ============================================================================

@pytest.fixture
def sample_pronunciation_result_excellent():
    """Fixture for excellent pronunciation result"""
    return {
        "recognized_text": "beautiful",
        "pronunciation_score": 95,
        "accuracy_score": 94,
        "fluency_score": 96,
        "completeness_score": 95,
        "words": [
            {
                "word": "beautiful",
                "accuracy_score": 94,
                "error_type": None,
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
def sample_pronunciation_result_good():
    """Fixture for good pronunciation result"""
    return {
        "recognized_text": "comfortable",
        "pronunciation_score": 82,
        "accuracy_score": 80,
        "fluency_score": 85,
        "completeness_score": 83,
        "words": [
            {
                "word": "comfortable",
                "accuracy_score": 80,
                "error_type": None,
                "phonemes": [
                    {"phoneme": "k", "accuracy_score": 85},
                    {"phoneme": "ʌ", "accuracy_score": 78},
                    {"phoneme": "m", "accuracy_score": 82}
                ]
            }
        ]
    }


@pytest.fixture
def sample_pronunciation_result_needs_improvement():
    """Fixture for pronunciation result that needs improvement"""
    return {
        "recognized_text": "comfortable",
        "pronunciation_score": 65,
        "accuracy_score": 60,
        "fluency_score": 68,
        "completeness_score": 70,
        "words": [
            {
                "word": "comfortable",
                "accuracy_score": 60,
                "error_type": None,
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
        "recognized_text": "pronunciation",
        "pronunciation_score": 45,
        "accuracy_score": 40,
        "fluency_score": 48,
        "completeness_score": 47,
        "words": [
            {
                "word": "pronunciation",
                "accuracy_score": 40,
                "error_type": None,
                "phonemes": [
                    {"phoneme": "p", "accuracy_score": 50},
                    {"phoneme": "r", "accuracy_score": 35},
                    {"phoneme": "ə", "accuracy_score": 42},
                    {"phoneme": "n", "accuracy_score": 45}
                ]
            }
        ]
    }


# ============================================================================
# Audio File Fixtures
# ============================================================================

@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing"""
    from io import BytesIO

    # Create a minimal WAV file structure (44 bytes header + some data)
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk size
        0x01, 0x00,              # Audio format (PCM)
        0x01, 0x00,              # Number of channels (mono)
        0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
        0x88, 0x58, 0x01, 0x00,  # Byte rate
        0x02, 0x00,              # Block align
        0x10, 0x00,              # Bits per sample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00,  # Data size
    ])

    audio_data = BytesIO(wav_header)
    audio_data.name = "test_audio.wav"
    audio_data.seek(0)

    return audio_data


# ============================================================================
# Progress Fixtures
# ============================================================================

@pytest.fixture
def sample_student_progress(test_db, test_student):
    """Create sample student progress records"""
    from datetime import date
    from decimal import Decimal

    today = date.today()
    progress_records = []

    # Create progress for last 7 days with varying scores
    for i in range(7):
        progress_date = today - timedelta(days=i)
        progress = StudentProgress(
            student_id=test_student.id,
            date=progress_date,
            words_practiced=3 + i,
            total_attempts=5 + i,
            average_score=Decimal(str(75 + i * 2))
        )
        test_db.add(progress)
        progress_records.append(progress)

    test_db.commit()
    return progress_records


# ============================================================================
# Validation Fixtures
# ============================================================================

@pytest.fixture
def valid_user_credentials():
    """Valid user registration/login credentials"""
    return {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass123!",
        "role": "student"
    }


@pytest.fixture
def invalid_credentials_missing_email():
    """Invalid credentials - missing email"""
    return {
        "username": "newuser",
        "password": "SecurePass123!",
        "role": "student"
    }


@pytest.fixture
def invalid_credentials_weak_password():
    """Invalid credentials - weak password"""
    return {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "123",
        "role": "student"
    }
