"""Locust load tests for TradePilot API.

Run: locust -f locustfile.py --host=http://localhost:8000
Or against Railway: locust -f locustfile.py --host=https://web-production-f8308.up.railway.app

Headless: locust -f locustfile.py --host=URL --users 20 --spawn-rate 5 --run-time 60s --headless
"""

import os

from locust import HttpUser, task, between


class TradePilotUser(HttpUser):
    """Simulates a user hitting TradePilot endpoints."""

    wait_time = between(1, 3)

    def on_start(self):
        """Optional: sign in to get token for protected routes."""
        self.token = None
        if os.environ.get("LOCUST_AUTH"):
            # Set LOCUST_AUTH=1 and LOCUST_EMAIL/LOCUST_PASSWORD to test auth flows
            email = os.environ.get("LOCUST_EMAIL", "test@example.com")
            password = os.environ.get("LOCUST_PASSWORD", "TestPass123!")
            r = self.client.post(
                "/api/auth/signin",
                json={"email": email, "password": password},
                name="/api/auth/signin",
            )
            if r.status_code == 200:
                data = r.json()
                self.token = data.get("token")

    @task(3)
    def health(self):
        """Public health - most frequent."""
        self.client.get("/api/test/trading-health", name="/api/test/trading-health")

    @task(3)
    def status(self):
        """Public status endpoint."""
        self.client.get("/api/status", name="/api/status")

    @task(2)
    def landing(self):
        """Landing page."""
        self.client.get("/landing", name="/landing")

    @task(1)
    def signin_page(self):
        """Sign-in page."""
        self.client.get("/signin", name="/signin")

    @task(1)
    def protected_settings(self):
        """Protected settings - 401 without auth is expected."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        with self.client.get(
            "/api/settings", headers=headers, name="/api/settings", catch_response=True
        ) as r:
            if r.status_code in (200, 401):
                r.success()
