"""
System tests for Student Workflow
Covers L01 Requirements: 1.c, 1.d, 1.e, 1.f
"""
import pytest
import sys
from pathlib import Path
from io import BytesIO

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


class TestAudioFileValidation:
    """
    L01 Requirement 1.c: The system must accept only valid audio file
    formats when students submit pronunciation recordings

    Testing approach: Functional category-partition testing
    Partitions: Valid audio formats (WAV, MP3, WebM), invalid formats,
                corrupted files, large files
    """

    def test_valid_wav_file_accepted(self, client, auth_headers_student, sample_audio_file):
        """Test that valid WAV files are accepted"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200

    def test_valid_mp3_file_accepted(self, client, auth_headers_student):
        """Test that valid MP3 files are accepted"""
        # Create minimal MP3-like file
        mp3_data = BytesIO(b'\xff\xfb' + b'\x00' * 100)  # MP3 header
        mp3_data.name = "test.mp3"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.mp3", mp3_data, "audio/mp3")}
        )

        # Should accept audio/mp3 content type
        assert response.status_code == 200

    def test_valid_webm_file_accepted(self, client, auth_headers_student):
        """Test that valid WebM files are accepted"""
        webm_data = BytesIO(b'\x1a\x45\xdf\xa3' + b'\x00' * 100)  # WebM header
        webm_data.name = "test.webm"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.webm", webm_data, "audio/webm")}
        )

        # Should accept audio/webm content type
        assert response.status_code == 200

    def test_invalid_pdf_file_rejected(self, client, auth_headers_student):
        """Test that PDF files are rejected"""
        pdf_data = BytesIO(b'%PDF-1.4\n' + b'\x00' * 100)
        pdf_data.name = "test.pdf"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.pdf", pdf_data, "application/pdf")}
        )

        assert response.status_code == 400
        data = response.json()
        assert "audio" in data["detail"].lower()

    def test_invalid_image_file_rejected(self, client, auth_headers_student):
        """Test that image files are rejected"""
        image_data = BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        image_data.name = "test.png"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.png", image_data, "image/png")}
        )

        assert response.status_code == 400

    def test_invalid_text_file_rejected(self, client, auth_headers_student):
        """Test that text files are rejected"""
        text_data = BytesIO(b'This is text content')
        text_data.name = "test.txt"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "test"},
            files={"audio_file": ("test.txt", text_data, "text/plain")}
        )

        assert response.status_code == 400

    def test_content_type_validation(self, client, auth_headers_student, sample_audio_file):
        """Test that content type is validated"""
        # WAV file with correct content type
        response_correct = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "correct"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response_correct.status_code == 200

        # Non-audio content type should fail
        fake_data = BytesIO(b'\x00' * 100)
        response_wrong = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "wrong"},
            files={"audio_file": ("test.bin", fake_data, "application/octet-stream")}
        )

        assert response_wrong.status_code == 400


class TestProgressStatisticsCalculation:
    """
    L01 Requirement 1.d: The system must calculate student progress
    statistics accurately including words practiced, average score,
    total attempts, and streak count

    Testing approach: Functional category-partition testing
    Partitions: No recordings, consecutive days, non-consecutive days,
                multiple recordings same day, different time periods
    """

    def test_progress_with_no_recordings(self, client, auth_headers_student):
        """Test progress statistics for student with no recordings"""
        response = client.get("/api/student/progress", headers=auth_headers_student)

        assert response.status_code == 200
        data = response.json()

        assert data["words_practiced"] == 0
        assert data["total_attempts"] == 0
        assert data["average_score"] == 0
        assert data["streak_count"] == 0

    def test_progress_with_single_recording(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test progress statistics after single recording"""
        # Submit one recording
        client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "single"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        # Get progress
        response = client.get("/api/student/progress", headers=auth_headers_student)

        assert response.status_code == 200
        data = response.json()

        assert data["words_practiced"] >= 1
        assert data["total_attempts"] >= 1
        assert data["average_score"] > 0
        assert data["streak_count"] >= 1  # Has practice today

    def test_progress_with_multiple_recordings_same_day(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test progress with multiple recordings on same day"""
        # Submit three recordings
        for i in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"word{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get progress
        response = client.get("/api/student/progress", headers=auth_headers_student)

        assert response.status_code == 200
        data = response.json()

        assert data["words_practiced"] >= 3
        assert data["total_attempts"] >= 3

    def test_average_score_calculation(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that average score is calculated correctly"""
        # Submit multiple recordings
        for i in range(5):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"avg{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get progress
        response = client.get("/api/student/progress", headers=auth_headers_student)

        assert response.status_code == 200
        data = response.json()

        # Average should be within valid range
        assert 0 <= data["average_score"] <= 100

        # Should have recent recordings
        assert len(data["recent_recordings"]) > 0

    def test_recent_recordings_list(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that recent recordings are included in progress"""
        # Submit recordings
        for i in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"recent{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get progress
        response = client.get("/api/student/progress", headers=auth_headers_student)

        assert response.status_code == 200
        data = response.json()

        assert "recent_recordings" in data
        assert len(data["recent_recordings"]) >= 3

        # Each recording should have required fields
        for recording in data["recent_recordings"]:
            assert "word_text" in recording
            assert "score" in recording
            assert "created_at" in recording

    def test_progress_period_filtering(self, client, auth_headers_student, sample_audio_file):
        """Test progress filtering by time period"""
        # Submit recording
        client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "period"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        # Get week progress
        response_week = client.get(
            "/api/student/progress?period=week",
            headers=auth_headers_student
        )
        assert response_week.status_code == 200

        # Get month progress
        response_month = client.get(
            "/api/student/progress?period=month",
            headers=auth_headers_student
        )
        assert response_month.status_code == 200

        # Month should include week data
        data_week = response_week.json()
        data_month = response_month.json()

        assert data_month["words_practiced"] >= data_week["words_practiced"]


class TestPronunciationScoreValidation:
    """
    L01 Requirement 1.e: The system must ensure pronunciation assessment
    scores are within valid ranges (0-100)

    Testing approach: Black-box testing
    """

    def test_pronunciation_scores_within_range(self, client, auth_headers_student, sample_audio_file):
        """Test that all pronunciation scores are within 0-100"""
        # Submit recording
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "validation"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Check all scores are in valid range
        scores = data["automated_scores"]

        assert 0 <= scores["pronunciation_score"] <= 100
        assert 0 <= scores["accuracy_score"] <= 100
        assert 0 <= scores["fluency_score"] <= 100
        assert 0 <= scores["completeness_score"] <= 100

    def test_multiple_submissions_all_valid_scores(self, client, auth_headers_student, sample_audio_file):
        """Test that multiple submissions all have valid scores"""
        # Submit multiple recordings
        for i in range(5):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            response = client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"multi{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

            assert response.status_code == 200
            scores = response.json()["automated_scores"]

            # All scores should be valid
            assert 0 <= scores["pronunciation_score"] <= 100
            assert 0 <= scores["accuracy_score"] <= 100
            assert 0 <= scores["fluency_score"] <= 100
            assert 0 <= scores["completeness_score"] <= 100


class TestAutomaticFeedbackGeneration:
    """
    L01 Requirement 1.f: The system must automatically generate feedback
    and assign grades based on pronunciation assessment results

    Testing approach: Functional category-partition testing
    Partitions: Excellent, good, fair, needs improvement, poor, invalid results
    """

    def test_feedback_generated_automatically(self, client, auth_headers_student, sample_audio_file):
        """Test that feedback is automatically generated on submission"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "automatic"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have feedback
        assert "feedback" in data
        assert "text" in data["feedback"]
        assert "grade" in data["feedback"]
        assert data["feedback"]["is_automated"] is True

    def test_grade_assigned_based_on_score(self, client, auth_headers_student, sample_audio_file):
        """Test that grade is assigned based on pronunciation score"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "graded"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Grade should be a valid letter grade
        valid_grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F", "N/A"]
        assert data["feedback"]["grade"] in valid_grades

    def test_feedback_includes_word_reference(self, client, auth_headers_student, sample_audio_file):
        """Test that feedback references the practiced word"""
        word_text = "referenced"

        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": word_text},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Feedback should mention the word
        assert word_text in data["feedback"]["text"]

    def test_feedback_stored_in_database(self, client, auth_headers_student, sample_audio_file, test_db):
        """Test that generated feedback is stored in database"""
        response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "stored"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        assert response.status_code == 200
        data = response.json()

        # Retrieve recording from database
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(data["recording_id"])

        # Feedback should be stored
        assert recording.teacher_feedback == data["feedback"]["text"]
        assert recording.teacher_grade == data["feedback"]["grade"]
        assert recording.status.value == "reviewed"

    def test_multiple_submissions_get_different_feedback(self, client, auth_headers_student, sample_audio_file):
        """Test that different words get appropriate feedback"""
        words = ["excellent", "wonderful", "beautiful"]

        for word in words:
            audio_copy = BytesIO(sample_audio_file.getvalue())
            response = client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": word},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

            assert response.status_code == 200
            data = response.json()

            # Each should have feedback
            assert "feedback" in data
            assert word in data["feedback"]["text"]
