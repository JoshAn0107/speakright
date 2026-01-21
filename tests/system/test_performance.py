"""
Performance Tests - API Response Time Validation

Tests that verify API endpoints respond within acceptable time limits.
Target: All endpoints should respond in < 3 seconds (NFR1 requirement).
"""
import pytest
import time


class TestAPIPerformance:
    """Performance tests for API response times"""

    MAX_RESPONSE_TIME = 3.0  # seconds (NFR1 requirement)

    # ========================================================================
    # Authentication Endpoint Performance
    # ========================================================================

    def test_login_response_time(self, client, test_student):
        """Login endpoint should respond within time limit"""
        start = time.time()
        response = client.post("/api/auth/login", json={
            "email": "student@test.com",
            "password": "password123"
        })
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < self.MAX_RESPONSE_TIME, f"Login took {elapsed:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"

    def test_register_response_time(self, client):
        """Registration endpoint should respond within time limit"""
        start = time.time()
        response = client.post("/api/auth/register", json={
            "username": "perftest_user",
            "email": "perftest@test.com",
            "password": "SecurePass123!",
            "role": "student"
        })
        elapsed = time.time() - start

        assert response.status_code == 201
        assert elapsed < self.MAX_RESPONSE_TIME, f"Register took {elapsed:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"

    # ========================================================================
    # Student Endpoint Performance
    # ========================================================================

    def test_get_recordings_response_time(self, client, auth_headers_student, sample_recording):
        """Get recordings endpoint should respond within time limit"""
        start = time.time()
        response = client.get("/api/student/recordings", headers=auth_headers_student)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < self.MAX_RESPONSE_TIME, f"Get recordings took {elapsed:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"

    def test_get_progress_response_time(self, client, auth_headers_student, sample_student_progress):
        """Get progress endpoint should respond within time limit"""
        start = time.time()
        response = client.get("/api/student/progress?period=week", headers=auth_headers_student)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < self.MAX_RESPONSE_TIME, f"Get progress took {elapsed:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"

    # ========================================================================
    # Words Endpoint Performance
    # ========================================================================

    def test_daily_challenge_response_time(self, client, auth_headers_student):
        """Daily challenge endpoint should respond within time limit"""
        start = time.time()
        response = client.get("/api/words/daily/challenge", headers=auth_headers_student)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < self.MAX_RESPONSE_TIME, f"Daily challenge took {elapsed:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"

    # ========================================================================
    # Health Check Performance
    # ========================================================================

    def test_health_check_response_time(self, client):
        """Health check should respond very quickly (< 1 second)"""
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check took {elapsed:.2f}s, expected < 1.0s"

    def test_root_endpoint_response_time(self, client):
        """Root endpoint should respond very quickly (< 1 second)"""
        start = time.time()
        response = client.get("/")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Root endpoint took {elapsed:.2f}s, expected < 1.0s"


class TestConcurrentRequests:
    """Basic concurrency tests"""

    def test_multiple_sequential_requests(self, client, test_student):
        """Multiple sequential requests should all respond within time limit"""
        total_requests = 5
        max_total_time = 10.0  # 5 requests should complete in < 10 seconds

        start = time.time()
        for _ in range(total_requests):
            response = client.post("/api/auth/login", json={
                "email": "student@test.com",
                "password": "password123"
            })
            assert response.status_code == 200
        elapsed = time.time() - start

        assert elapsed < max_total_time, f"{total_requests} requests took {elapsed:.2f}s, expected < {max_total_time}s"
        avg_time = elapsed / total_requests
        assert avg_time < 3.0, f"Average response time {avg_time:.2f}s exceeds limit"
