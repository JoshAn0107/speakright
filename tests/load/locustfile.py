"""
Load Testing with Locust - Non-Functional Requirements Validation

This tests NFR1: API response time < 3 seconds under load
Demonstrates load testing techniques for LO3 (testing techniques)

Usage:
  locust -f tests/load/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 30s

  -u 10: 10 concurrent users
  -r 2: spawn 2 users per second
  -t 30s: run for 30 seconds
"""

from locust import HttpUser, task, between
import random
import string


class SpeakRightUser(HttpUser):
    """Simulates a typical user interacting with the SpeakRight API"""

    # Wait 1-3 seconds between tasks (realistic user behavior)
    wait_time = between(1, 3)

    # Store auth token after login
    token = None
    user_id = None

    def on_start(self):
        """Called when a simulated user starts - register and login"""
        # Generate unique user for this load test session
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
        self.email = f"loadtest_{random_suffix}@test.com"
        self.password = "LoadTest123!"
        self.username = f"loaduser_{random_suffix}"

        # Register
        register_response = self.client.post("/api/auth/register", json={
            "email": self.email,
            "password": self.password,
            "username": self.username,
            "role": "student"
        })

        if register_response.status_code == 201:
            # Login to get token
            login_response = self.client.post("/api/auth/login", json={
                "email": self.email,
                "password": self.password
            })

            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")

    def get_auth_headers(self):
        """Get authorization headers if logged in"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    # =========================================================================
    # Public Endpoints (No Auth Required)
    # =========================================================================

    @task(3)
    def health_check(self):
        """Test health endpoint - should be very fast"""
        with self.client.get("/health", catch_response=True) as response:
            if response.elapsed.total_seconds() > 1:
                response.failure(f"Health check too slow: {response.elapsed.total_seconds():.2f}s")

    @task(2)
    def root_endpoint(self):
        """Test root endpoint"""
        self.client.get("/")

    @task(3)
    def get_daily_challenge(self):
        """Test daily challenge endpoint - public"""
        with self.client.get("/api/words/daily/challenge", catch_response=True) as response:
            if response.elapsed.total_seconds() > 3:
                response.failure(f"Daily challenge too slow: {response.elapsed.total_seconds():.2f}s (NFR1 violated)")

    # =========================================================================
    # Authenticated Endpoints
    # =========================================================================

    @task(5)
    def get_student_progress(self):
        """Test student progress endpoint - requires auth"""
        if not self.token:
            return

        with self.client.get(
            "/api/student/progress",
            headers=self.get_auth_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 401:
                response.failure("Unauthorized - token may have expired")
            elif response.elapsed.total_seconds() > 3:
                response.failure(f"Progress endpoint too slow: {response.elapsed.total_seconds():.2f}s (NFR1 violated)")

    @task(4)
    def get_recordings(self):
        """Test recordings list endpoint"""
        if not self.token:
            return

        with self.client.get(
            "/api/student/recordings",
            headers=self.get_auth_headers(),
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 3:
                response.failure(f"Recordings endpoint too slow: {response.elapsed.total_seconds():.2f}s (NFR1 violated)")

    @task(2)
    def get_assignments(self):
        """Test assignments endpoint"""
        if not self.token:
            return

        self.client.get(
            "/api/assignments/student/assignments",
            headers=self.get_auth_headers()
        )


class QuickLoadTest(HttpUser):
    """Lighter load test for CI pipeline - only tests public endpoints"""

    wait_time = between(0.5, 1)

    @task(5)
    def health_check(self):
        """Quick health check"""
        self.client.get("/health")

    @task(3)
    def root_endpoint(self):
        """Root endpoint"""
        self.client.get("/")

    @task(2)
    def daily_challenge(self):
        """Daily challenge - public"""
        self.client.get("/api/words/daily/challenge")
