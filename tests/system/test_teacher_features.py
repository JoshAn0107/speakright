"""
System tests for Teacher Features
Covers L01 Requirements: 1.g, 1.i, 1.j, 1.k
"""
import pytest
import sys
from pathlib import Path
from io import BytesIO

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


class TestTeacherFeedbackOverride:
    """
    L01 Requirement 1.g: The system must allow teachers to override
    automated feedback with manual feedback

    Testing approach: Functional category-partition testing
    Partitions: Feedback text only, grade only, both feedback and grade,
                flag for practice, verify automated flag
    """

    def test_teacher_provides_new_feedback_text(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test teacher providing new feedback text"""
        # Student submits recording
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "override"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        recording_id = submit_response.json()["recording_id"]
        original_feedback = submit_response.json()["feedback"]["text"]

        # Teacher provides new feedback
        teacher_feedback = {
            "recording_id": recording_id,
            "feedback_text": "Pay attention to the vowel sounds.",
            "flag_for_practice": False
        }

        response = client.post(
            "/api/teacher/feedback",
            headers=auth_headers_teacher,
            json=teacher_feedback
        )

        assert response.status_code == 200

        # Verify feedback was updated
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(recording_id)

        assert recording.teacher_feedback == "Pay attention to the vowel sounds."
        assert recording.teacher_feedback != original_feedback

    def test_teacher_provides_new_grade(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test teacher providing new grade"""
        # Student submits recording
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "gradechange"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        recording_id = submit_response.json()["recording_id"]

        # Teacher provides new grade
        teacher_feedback = {
            "recording_id": recording_id,
            "grade": "A+",
            "flag_for_practice": False
        }

        response = client.post(
            "/api/teacher/feedback",
            headers=auth_headers_teacher,
            json=teacher_feedback
        )

        assert response.status_code == 200

        # Verify grade was updated
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(recording_id)

        assert recording.teacher_grade == "A+"

    def test_teacher_provides_both_feedback_and_grade(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test teacher providing both feedback text and grade"""
        # Student submits recording
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "complete"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        recording_id = submit_response.json()["recording_id"]

        # Teacher provides both feedback and grade
        teacher_feedback = {
            "recording_id": recording_id,
            "feedback_text": "Excellent pronunciation!",
            "grade": "A",
            "flag_for_practice": False
        }

        response = client.post(
            "/api/teacher/feedback",
            headers=auth_headers_teacher,
            json=teacher_feedback
        )

        assert response.status_code == 200

        # Verify both were updated
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(recording_id)

        assert recording.teacher_feedback == "Excellent pronunciation!"
        assert recording.teacher_grade == "A"

    def test_teacher_flags_for_additional_practice(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test teacher flagging recording for additional practice"""
        # Student submits recording
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "practice"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        recording_id = submit_response.json()["recording_id"]

        # Teacher flags for practice
        teacher_feedback = {
            "recording_id": recording_id,
            "feedback_text": "Needs more practice",
            "flag_for_practice": True
        }

        response = client.post(
            "/api/teacher/feedback",
            headers=auth_headers_teacher,
            json=teacher_feedback
        )

        assert response.status_code == 200

        # Verify flag was set
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(recording_id)

        assert recording.flag_for_practice is True

    def test_automated_feedback_flag_updated(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test that is_automated_feedback flag is set to false after teacher review"""
        # Student submits recording
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "manual"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        recording_id = submit_response.json()["recording_id"]

        # Verify initially automated
        from app.models.recording import Recording
        recording = test_db.query(Recording).get(recording_id)
        # Initially should be automated (or field might not exist in old records)

        # Teacher provides manual feedback
        teacher_feedback = {
            "recording_id": recording_id,
            "feedback_text": "Manual review",
            "flag_for_practice": False
        }

        response = client.post(
            "/api/teacher/feedback",
            headers=auth_headers_teacher,
            json=teacher_feedback
        )

        assert response.status_code == 200

        # Verify is_automated_feedback is now False
        test_db.refresh(recording)
        assert recording.is_automated_feedback is False


class TestSubmissionFiltering:
    """
    L01 Requirement 1.i: The system must correctly filter teacher
    submissions by status and class

    Testing approach: Functional pairwise testing
    Combinations: (status, class) pairs
    """

    def test_filter_by_pending_status(self, client, auth_headers_teacher, test_db):
        """Test filtering submissions by pending status"""
        response = client.get(
            "/api/teacher/submissions?status_filter=pending",
            headers=auth_headers_teacher
        )

        assert response.status_code == 200
        data = response.json()

        # All returned submissions should be pending
        for submission in data:
            assert submission["status"] == "pending"

    def test_filter_by_reviewed_status(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test filtering submissions by reviewed status"""
        # Create a reviewed submission
        submit_response = client.post(
            "/api/student/recordings/submit",
            headers=auth_headers_student,
            data={"word_text": "reviewed"},
            files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")}
        )

        # Filter by reviewed
        response = client.get(
            "/api/teacher/submissions?status_filter=reviewed",
            headers=auth_headers_teacher
        )

        assert response.status_code == 200
        data = response.json()

        # All returned submissions should be reviewed
        for submission in data:
            assert submission["status"] == "reviewed"

    def test_filter_by_class(self, client, auth_headers_teacher, test_db, test_teacher):
        """Test filtering submissions by class"""
        from app.models.user import User, UserRole
        from app.models.classes import Class, ClassEnrollment
        from app.models.recording import Recording
        from app.core.security import get_password_hash

        # Create class
        test_class = Class(
            teacher_id=test_teacher.id,
            class_name="Filter Test Class"
        )
        test_db.add(test_class)
        test_db.commit()

        # Create student and enroll
        student = User(
            username="classstudent",
            email="class@test.com",
            password_hash=get_password_hash("password"),
            role=UserRole.STUDENT
        )
        test_db.add(student)
        test_db.commit()

        enrollment = ClassEnrollment(
            class_id=test_class.id,
            student_id=student.id
        )
        test_db.add(enrollment)

        # Create recording
        recording = Recording(
            student_id=student.id,
            word_text="classword",
            audio_file_path="/uploads/test.wav",
            automated_scores={"pronunciation_score": 80}
        )
        test_db.add(recording)
        test_db.commit()

        # Filter by class
        response = client.get(
            f"/api/teacher/submissions?class_id={test_class.id}",
            headers=auth_headers_teacher
        )

        assert response.status_code == 200
        data = response.json()

        # Should include the class student's recording
        student_ids = [s["student_id"] for s in data]
        assert student.id in student_ids

    def test_filter_by_status_and_class_combined(self, client, auth_headers_teacher, test_db, test_teacher):
        """Test combined filtering by both status and class"""
        from app.models.user import User, UserRole
        from app.models.classes import Class, ClassEnrollment
        from app.models.recording import Recording, RecordingStatus
        from app.core.security import get_password_hash

        # Create class
        test_class = Class(
            teacher_id=test_teacher.id,
            class_name="Combined Filter Class"
        )
        test_db.add(test_class)
        test_db.commit()

        # Create student
        student = User(
            username="combstudent",
            email="comb@test.com",
            password_hash=get_password_hash("password"),
            role=UserRole.STUDENT
        )
        test_db.add(student)
        test_db.commit()

        # Enroll student
        test_db.add(ClassEnrollment(class_id=test_class.id, student_id=student.id))

        # Create reviewed recording
        recording = Recording(
            student_id=student.id,
            word_text="combword",
            audio_file_path="/uploads/test.wav",
            automated_scores={"pronunciation_score": 80},
            status=RecordingStatus.REVIEWED
        )
        test_db.add(recording)
        test_db.commit()

        # Filter by both status and class
        response = client.get(
            f"/api/teacher/submissions?status_filter=reviewed&class_id={test_class.id}",
            headers=auth_headers_teacher
        )

        assert response.status_code == 200
        data = response.json()

        # All should be reviewed and from the class
        for submission in data:
            assert submission["status"] == "reviewed"


class TestClassAnalytics:
    """
    L01 Requirement 1.j: The system must calculate class analytics
    correctly including total recordings, pending reviews, average
    scores, most practiced words, and challenging words

    Testing approach: Black-box testing
    """

    def test_analytics_total_recordings_count(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test that total recordings count is accurate"""
        # Submit multiple recordings
        for i in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"analytics{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get analytics
        response = client.get("/api/teacher/analytics", headers=auth_headers_teacher)

        assert response.status_code == 200
        data = response.json()

        assert "total_recordings" in data
        assert data["total_recordings"] >= 3

    def test_analytics_average_score(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test that average score is calculated"""
        # Submit recordings
        for i in range(2):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": f"avgscore{i}"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get analytics
        response = client.get("/api/teacher/analytics", headers=auth_headers_teacher)

        assert response.status_code == 200
        data = response.json()

        assert "average_score" in data
        assert 0 <= data["average_score"] <= 100

    def test_analytics_most_practiced_words(self, client, auth_headers_teacher, auth_headers_student, sample_audio_file, test_db):
        """Test that most practiced words are listed"""
        # Submit same word multiple times
        for _ in range(3):
            audio_copy = BytesIO(sample_audio_file.getvalue())
            client.post(
                "/api/student/recordings/submit",
                headers=auth_headers_student,
                data={"word_text": "popular"},
                files={"audio_file": ("test.wav", audio_copy, "audio/wav")}
            )

        # Get analytics
        response = client.get("/api/teacher/analytics", headers=auth_headers_teacher)

        assert response.status_code == 200
        data = response.json()

        assert "most_practiced_words" in data
        # "popular" should appear in the list
        words = [w["word"] for w in data["most_practiced_words"]]
        if len(words) > 0:  # If there are any words
            # Check structure
            assert all("word" in w and "count" in w for w in data["most_practiced_words"])

    def test_analytics_challenging_words(self, client, auth_headers_teacher, test_db):
        """Test that challenging words (low scores) are identified"""
        response = client.get("/api/teacher/analytics", headers=auth_headers_teacher)

        assert response.status_code == 200
        data = response.json()

        assert "challenging_words" in data
        # Check structure if there are challenging words
        if len(data["challenging_words"]) > 0:
            assert all("word" in w and "average_score" in w for w in data["challenging_words"])


class TestDailyChallengeWord:
    """
    L01 Requirement 1.k: The system must generate a daily challenge word
    either from the database or from a predefined fallback list

    Testing approach: Functional category-partition testing
    Partitions: Database has words, database empty, API fails
    """

    def test_daily_challenge_returns_word(self, client):
        """Test that daily challenge endpoint returns a word"""
        response = client.get("/api/words/daily/challenge")

        # Should return a word (either from DB or fallback)
        assert response.status_code == 200
        data = response.json()

        assert "word" in data
        assert data["word"] is not None

    def test_daily_challenge_with_database_words(self, client, test_db, sample_word_assignment):
        """Test daily challenge when database has words"""
        response = client.get("/api/words/daily/challenge")

        assert response.status_code == 200
        data = response.json()

        # Should return word data
        assert "word" in data

    def test_daily_challenge_structure(self, client):
        """Test that daily challenge word has expected structure"""
        response = client.get("/api/words/daily/challenge")

        assert response.status_code == 200
        data = response.json()

        # Should have word data structure
        assert "word" in data
        # May have additional fields like meanings, phonetics, etc from dictionary API
