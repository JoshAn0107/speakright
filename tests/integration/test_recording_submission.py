"""
Integration tests for Recording Submission
Covers L01 Requirements: 2.a, 2.e, 2.h
"""
import pytest
import sys
from pathlib import Path
from io import BytesIO
from datetime import date
from decimal import Decimal

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.recording import Recording, RecordingStatus
from app.models.word import WordAssignment
from app.models.progress import StudentProgress


class TestRecordingSubmissionIntegration:
    """
    L01 Requirement 2.a: When the submit_recording endpoint is called,
    the system must integrate pronunciation assessment service and
    feedback generation service correctly

    Testing approach: Black-box testing
    """

    def test_recording_submission_creates_database_entry(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that submitting a recording creates a database entry"""
        # Submit recording
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "beautiful"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Verify database entry was created
        recording = test_db.query(Recording).filter(Recording.word_text == "beautiful").first()
        assert recording is not None
        assert recording.automated_scores is not None
        assert recording.teacher_feedback is not None

    def test_pronunciation_assessment_integration(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that pronunciation assessment service is called and results are stored"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "wonderful"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have automated scores
        assert "automated_scores" in data
        assert data["automated_scores"] is not None

        # Scores should be within valid range
        assert 0 <= data["automated_scores"]["pronunciation_score"] <= 100

        # Verify scores are in database
        recording = test_db.query(Recording).filter(Recording.word_text == "wonderful").first()
        assert recording.automated_scores["pronunciation_score"] == data["automated_scores"]["pronunciation_score"]

    def test_feedback_generation_integration(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that feedback generation service is called and results are stored"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have feedback
        assert "feedback" in data
        assert "text" in data["feedback"]
        assert "grade" in data["feedback"]
        assert data["feedback"]["is_automated"] is True

        # Verify feedback is in database
        recording = test_db.query(Recording).filter(Recording.word_text == "test").first()
        assert recording.teacher_feedback == data["feedback"]["text"]
        assert recording.teacher_grade == data["feedback"]["grade"]

    def test_complete_submission_flow(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test complete flow: audio upload -> assessment -> feedback -> database"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "complete"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Response should have all components
        assert "recording_id" in data
        assert "automated_scores" in data
        assert "feedback" in data

        # Database should have complete record
        recording = test_db.query(Recording).get(data["recording_id"])
        assert recording is not None
        assert recording.audio_file_path is not None
        assert recording.automated_scores is not None
        assert recording.teacher_feedback is not None
        assert recording.teacher_grade is not None
        assert recording.status == RecordingStatus.REVIEWED


class TestMultiTableUpdates:
    """
    L01 Requirement 2.e: The system must correctly update both recording
    and word assignment records when a student submits a pronunciation recording

    Testing approach: Black-box testing
    """

    def test_creates_recording_entry(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that recording entry is created"""
        word_text = "integration"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": word_text},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Verify recording was created
        recording = test_db.query(Recording).filter(Recording.word_text == word_text).first()
        assert recording is not None

    def test_updates_existing_word_assignment(self, client, auth_headers_student, sample_audio_file, test_db, sample_word_assignment):
        """Test that existing word assignment practice count is incremented"""
        initial_count = sample_word_assignment.times_practiced
        word_text = sample_word_assignment.word_text

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": word_text},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Verify practice count was incremented
        test_db.refresh(sample_word_assignment)
        assert sample_word_assignment.times_practiced == initial_count + 1

    def test_creates_new_word_assignment_if_not_exists(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that new word assignment is created if word doesn't exist"""
        word_text = "newword"

        # Verify word doesn't exist initially
        assert test_db.query(WordAssignment).filter(WordAssignment.word_text == word_text).first() is None

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": word_text},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Verify word assignment was created
        word_assignment = test_db.query(WordAssignment).filter(WordAssignment.word_text == word_text).first()
        assert word_assignment is not None
        assert word_assignment.times_practiced == 1

    def test_atomic_transaction_both_tables_updated(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that both tables are updated in same transaction"""
        word_text = "atomic"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": word_text},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Both recording and word assignment should exist
        recording = test_db.query(Recording).filter(Recording.word_text == word_text).first()
        word_assignment = test_db.query(WordAssignment).filter(WordAssignment.word_text == word_text).first()

        assert recording is not None
        assert word_assignment is not None

    def test_multiple_submissions_increment_count(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that multiple submissions for same word increment count correctly"""
        word_text = "repeated"

        # Submit 3 times
        for i in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            audio_copy.name = "test.wav"

            response = client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": word_text},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )
            assert response.status_code == 200

        # Verify practice count
        word_assignment = test_db.query(WordAssignment).filter(WordAssignment.word_text == word_text).first()
        assert word_assignment.times_practiced == 3

        # Verify 3 recordings exist
        recording_count = test_db.query(Recording).filter(Recording.word_text == word_text).count()
        assert recording_count == 3


class TestProgressCalculationIntegration:
    """
    L01 Requirement 2.h: When updating student progress, the system must
    correctly calculate running average scores across multiple recordings

    Testing approach: Black-box testing
    """

    def test_creates_progress_entry_for_first_recording(self, client, auth_headers_student, sample_audio_file, test_db, test_student):
        """Test that progress entry is created on first recording of the day"""
        today = date.today()

        # Verify no progress entry exists
        assert test_db.query(StudentProgress).filter(
            StudentProgress.student_id == test_student.id,
            StudentProgress.date == today
        ).first() is None

        # Submit recording
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "first"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

        # Verify progress entry was created
        progress = test_db.query(StudentProgress).filter(
            StudentProgress.student_id == test_student.id,
            StudentProgress.date == today
        ).first()

        assert progress is not None
        assert progress.words_practiced == 1
        assert progress.total_attempts == 1

    def test_updates_existing_progress_entry(self, client, auth_headers_student, sample_audio_file, test_db, test_student):
        """Test that existing progress entry is updated on subsequent recordings"""
        today = date.today()

        # Submit first recording
        response1 = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "word1"},
            files={"audio_file": ("test.wav", BytesIO(sample_audio_file.getvalue()), "audio/wav")}
        )
        assert response1.status_code == 200

        # Get progress after first recording
        progress = test_db.query(StudentProgress).filter(
            StudentProgress.student_id == test_student.id,
            StudentProgress.date == today
        ).first()
        first_attempts = progress.total_attempts

        # Submit second recording
        response2 = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "word2"},
            files={"audio_file": ("test.wav", BytesIO(sample_audio_file.getvalue()), "audio/wav")}
        )
        assert response2.status_code == 200

        # Verify progress was updated
        test_db.refresh(progress)
        assert progress.total_attempts == first_attempts + 1
        assert progress.words_practiced == 2

    def test_running_average_calculation(self, client, auth_headers_student, sample_audio_file, test_db, test_student):
        """Test that running average is calculated correctly"""
        today = date.today()

        # We can't control exact scores in mock, but we can verify the calculation
        # Submit multiple recordings
        for i in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())

            response = client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"word{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )
            assert response.status_code == 200

        # Get progress
        progress = test_db.query(StudentProgress).filter(
            StudentProgress.student_id == test_student.id,
            StudentProgress.date == today
        ).first()

        assert progress is not None
        assert progress.total_attempts == 3

        # Get all recordings for today
        from app.models.recording import Recording
        recordings = test_db.query(Recording).filter(
            Recording.student_id == test_student.id
        ).all()

        # Calculate expected average manually
        scores = [r.automated_scores["pronunciation_score"] for r in recordings]
        expected_avg = Decimal(str(sum(scores) / len(scores)))

        # Verify calculated average (allow small rounding difference)
        assert abs(float(progress.average_score) - float(expected_avg)) < 1.0

    def test_average_score_precision(self, client, auth_headers_student, sample_audio_file, test_db, test_student):
        """Test that average score maintains proper decimal precision"""
        # Submit recording
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "precision"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )
        assert response.status_code == 200

        # Get progress
        progress = test_db.query(StudentProgress).filter(
            StudentProgress.student_id == test_student.id,
            StudentProgress.date == date.today()
        ).first()

        # Average score should be a Decimal
        assert isinstance(progress.average_score, Decimal)
        assert progress.average_score >= 0
        assert progress.average_score <= 100
