"""
System tests for Authentication
Covers L01 Requirements: 1.a, 1.b
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


class TestAuthenticationSystem:
    """
    L01 Requirement 1.a: The system must authenticate users correctly
    and issue valid JWT tokens upon successful login

    Testing approach: Functional category-partition testing
    Partitions: Valid credentials, invalid email, incorrect password,
                missing credentials, malformed input
    """

    def test_valid_credentials_successful_login(self, client, test_db):
        """Test successful authentication with valid credentials"""
        # Register user
        register_data = {
            "username": "validuser",
            "email": "valid@test.com",
            "password": "SecurePass123!",
            "role": "student"
        }

        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        # Login with valid credentials
        login_data = {
            "email": "valid@test.com",
            "password": "SecurePass123!"
        }

        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        data = login_response.json()

        # Should return token
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] is not None
        assert len(data["access_token"]) > 0

        # Should return user data
        assert "user" in data
        assert data["user"]["email"] == "valid@test.com"
        assert data["user"]["username"] == "validuser"

    def test_invalid_email_login_fails(self, client, test_db):
        """Test that invalid email fails authentication"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "unauthorized" in data["detail"].lower()

    def test_incorrect_password_login_fails(self, client, test_db):
        """Test that incorrect password fails authentication"""
        # Register user
        register_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "CorrectPass123!",
            "role": "student"
        }
        client.post("/api/auth/register", json=register_data)

        # Login with wrong password
        login_data = {
            "email": "test@test.com",
            "password": "WrongPass123!"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

    def test_missing_email_login_fails(self, client, test_db):
        """Test that missing email fails authentication"""
        login_data = {
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422  # Validation error

    def test_missing_password_login_fails(self, client, test_db):
        """Test that missing password fails authentication"""
        login_data = {
            "email": "test@test.com"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422  # Validation error

    def test_malformed_email_login_fails(self, client, test_db):
        """Test that malformed email fails authentication"""
        login_data = {
            "email": "not-an-email",
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)
        # Could be validation error (422) or auth failure (401)
        assert response.status_code in [401, 422]

    def test_case_sensitive_password(self, client, test_db):
        """Test that password authentication is case-sensitive"""
        # Register user
        register_data = {
            "username": "caseuser",
            "email": "case@test.com",
            "password": "MyPassword123!",
            "role": "student"
        }
        client.post("/api/auth/register", json=register_data)

        # Try login with different case
        login_data = {
            "email": "case@test.com",
            "password": "mypassword123!"  # Different case
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

    def test_jwt_token_can_access_protected_endpoints(self, client, test_db):
        """Test that JWT token allows access to protected endpoints"""
        # Register and login
        register_data = {
            "username": "protecteduser",
            "email": "protected@test.com",
            "password": "SecurePass123!",
            "role": "student"
        }
        client.post("/api/auth/register", json=register_data)

        login_response = client.post(
            "/api/auth/login",
            json={"email": "protected@test.com", "password": "SecurePass123!"}
        )

        token = login_response.json()["access_token"]

        # Try to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/student/progress", headers=headers)

        # Should succeed (200) or return data-related error, not auth error
        assert response.status_code != 401

    def test_registration_returns_token(self, client, test_db):
        """Test that registration also returns a valid JWT token"""
        register_data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "SecurePass123!",
            "role": "student"
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 201

        data = response.json()

        # Should return token
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Token should be valid
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        protected_response = client.get("/api/student/progress", headers=headers)
        assert protected_response.status_code != 401


class TestRoleBasedAccessControl:
    """
    L01 Requirement 1.b: The system must correctly validate user roles
    and enforce role-based access control

    Testing approach: Functional category-partition testing
    Partitions: Student accessing student endpoints, teacher accessing teacher endpoints,
                student attempting teacher endpoints, teacher attempting student endpoints,
                unauthenticated access
    """

    def test_student_can_access_student_endpoints(self, client, auth_headers_student):
        """Test that students can access student-only endpoints"""
        response = client.get("/api/student/progress", headers=auth_headers_student)

        # Should succeed or return data error, not auth error
        assert response.status_code != 401
        assert response.status_code != 403

    def test_teacher_can_access_teacher_endpoints(self, client, auth_headers_teacher):
        """Test that teachers can access teacher-only endpoints"""
        response = client.get("/api/teacher/submissions", headers=auth_headers_teacher)

        # Should succeed
        assert response.status_code == 200

    def test_student_cannot_access_teacher_endpoints(self, client, auth_headers_student):
        """Test that students cannot access teacher-only endpoints"""
        response = client.get("/api/teacher/submissions", headers=auth_headers_student)

        # Should be forbidden
        assert response.status_code in [401, 403]

    def test_teacher_can_access_student_endpoints(self, client, auth_headers_teacher):
        """Test that teachers can access student endpoints (if allowed by design)"""
        response = client.get("/api/student/progress", headers=auth_headers_teacher)

        # Depending on design, this might be allowed or forbidden
        # If your design forbids it, assert 403. If allowed, assert != 401
        # Adjust based on your actual RBAC design
        assert response.status_code in [200, 403]

    def test_unauthenticated_cannot_access_protected_endpoints(self, client):
        """Test that unauthenticated users cannot access protected endpoints"""
        # Try student endpoint
        response1 = client.get("/api/student/progress")
        assert response1.status_code == 401

        # Try teacher endpoint
        response2 = client.get("/api/teacher/submissions")
        assert response2.status_code == 401

    def test_invalid_token_denied_access(self, client):
        """Test that invalid tokens are rejected"""
        headers = {"Authorization": "Bearer invalid-token-12345"}

        response = client.get("/api/student/progress", headers=headers)
        assert response.status_code == 401

    def test_expired_token_denied_access(self, client, test_student):
        """Test that expired tokens are rejected"""
        from datetime import timedelta
        from app.core.security import create_access_token

        # Create token that expires immediately
        expired_token = create_access_token(
            data={"sub": str(test_student.id)},
            expires_delta=timedelta(seconds=-1)
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/student/progress", headers=headers)

        assert response.status_code == 401

    def test_malformed_authorization_header_denied(self, client):
        """Test that malformed authorization headers are rejected"""
        # Missing "Bearer" prefix
        headers1 = {"Authorization": "some-token"}
        response1 = client.get("/api/student/progress", headers=headers1)
        assert response1.status_code == 401

        # Empty token
        headers2 = {"Authorization": "Bearer "}
        response2 = client.get("/api/student/progress", headers=headers2)
        assert response2.status_code == 401

    def test_role_verification_for_word_assignment(self, client, auth_headers_student, auth_headers_teacher):
        """Test that only teachers can assign words"""
        word_data = {
            "word_text": "test",
            "difficulty_level": "beginner",
            "topic_tags": ["test"]
        }

        # Student should be denied
        student_response = client.post(
            "/api/words/assign",
            headers=auth_headers_student,
            json=word_data
        )
        assert student_response.status_code in [401, 403]

        # Teacher should be allowed (might fail for other reasons like dictionary API)
        teacher_response = client.post(
            "/api/words/assign",
            headers=auth_headers_teacher,
            json=word_data
        )
        # Should not be auth error
        assert teacher_response.status_code not in [401, 403]

    def test_role_persistence_across_requests(self, client, test_db):
        """Test that user role is correctly maintained across multiple requests"""
        # Register as student
        register_data = {
            "username": "persistuser",
            "email": "persist@test.com",
            "password": "SecurePass123!",
            "role": "student"
        }
        register_response = client.post("/api/auth/register", json=register_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make multiple requests
        for _ in range(3):
            response = client.get("/api/student/progress", headers=headers)
            assert response.status_code != 401

            # Should still be denied teacher access
            teacher_response = client.get("/api/teacher/submissions", headers=headers)
            assert teacher_response.status_code in [401, 403]
