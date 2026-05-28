"""
Performance testing with Locust
Load test for API endpoints
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json
import time


class RecommendationUser(HttpUser):
    """
    Simulates a user making recommendation requests
    """
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        # Get available locations and cuisines
        self.client.get("/api/locations")
        self.client.get("/api/cuisines")
    
    @task(3)
    def get_recommendations(self):
        """Get restaurant recommendations (most common task)"""
        payload = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_preferences": "family-friendly"
        }
        
        response = self.client.post(
            "/api/recommendations",
            json=payload,
            name="/api/recommendations"
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # Optionally get details for a restaurant
                recommendations = data.get("data", {}).get("recommendations", [])
                if recommendations:
                    restaurant_id = recommendations[0].get("id")
                    if restaurant_id:
                        self.client.get(f"/api/restaurant/{restaurant_id}")
    
    @task(1)
    def get_locations(self):
        """Get available locations"""
        self.client.get("/api/locations")
    
    @task(1)
    def get_cuisines(self):
        """Get available cuisines"""
        self.client.get("/api/cuisines")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/api/health")


class StressTestUser(HttpUser):
    """
    Simulates stress testing with rapid requests
    """
    wait_time = between(0.1, 0.5)
    
    @task
    def rapid_recommendations(self):
        """Rapid recommendation requests for stress testing"""
        payload = {
            "location": "Delhi",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0
        }
        
        self.client.post("/api/recommendations", json=payload)


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust initializes
    """
    print("Locust initialized for performance testing")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test stops
    """
    if isinstance(environment.runner, MasterRunner):
        print("Performance test completed")
        print(f"Total requests: {environment.runner.stats.total.num_requests}")
        print(f"Failures: {environment.runner.stats.total.num_failures}")
        print(f"Median response time: {environment.runner.stats.total.median_response_time}ms")
        print(f"95th percentile: {environment.runner.stats.total.get_response_time_percentile(0.95)}ms")
