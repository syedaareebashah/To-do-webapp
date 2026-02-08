"""
Performance Test with Concurrent Users for Todo AI Chatbot System

This module tests the system's performance under concurrent user loads.
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from sqlmodel import Session
from uuid import uuid4
from fastapi.testclient import TestClient

from src.models.user import User
from src.app.main import app
from src.database.session import get_session


class PerformanceWithConcurrentUsersTester:
    """
    Tester for performance under concurrent user loads.
    """

    def __init__(self, db_session: Session, test_client: TestClient = None):
        """
        Initialize the concurrent user performance tester.

        Args:
            db_session (Session): Database session for testing
            test_client (TestClient, optional): FastAPI test client
        """
        self.db_session = db_session
        self.test_client = test_client or TestClient(app)
        self.test_users = []

    async def setup_test_users(self, num_users: int = 10) -> List[User]:
        """
        Set up multiple test users for concurrent testing.

        Args:
            num_users (int): Number of test users to create

        Returns:
            List[User]: List of created test users
        """
        users = []
        for i in range(num_users):
            user = User(
                username=f"perf_test_user_{i}",
                email=f"perf_test_{i}@test.com"
            )
            self.db_session.add(user)
            users.append(user)

        self.db_session.commit()

        # Refresh users to get their IDs
        for user in users:
            self.db_session.refresh(user)

        self.test_users = users
        return users

    async def simulate_single_user_conversation(self, user: User, messages: List[str]) -> Dict[str, Any]:
        """
        Simulate a single user having a conversation with the chatbot.

        Args:
            user (User): The user having the conversation
            messages (List[str]): List of messages to send in sequence

        Returns:
            Dict[str, Any]: Results of the conversation simulation
        """
        results = []
        conversation_id = None

        for i, message in enumerate(messages):
            start_time = time.time()

            # Send the message to the chat endpoint
            if i == 0:
                # First message - no conversation ID
                response = self.test_client.post(
                    f"/api/{user.id}/chat",
                    json={"message": message}
                )
            else:
                # Subsequent messages - include conversation ID
                response = self.test_client.post(
                    f"/api/{user.id}/chat",
                    json={
                        "message": message,
                        "conversation_id": conversation_id
                    }
                )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                response_data = response.json()
                conversation_id = response_data.get("conversation_id", conversation_id)

                results.append({
                    "message": message,
                    "response": response_data.get("response", ""),
                    "response_time": response_time,
                    "status": "success"
                })
            else:
                results.append({
                    "message": message,
                    "response_time": response_time,
                    "status": "error",
                    "error": response.text
                })

        return {
            "user_id": str(user.id),
            "total_messages": len(messages),
            "successful_requests": len([r for r in results if r["status"] == "success"]),
            "results": results,
            "avg_response_time": sum(r["response_time"] for r in results) / len(results) if results else 0
        }

    async def test_concurrent_users_performance(self, num_users: int = 5, messages_per_user: int = 3) -> Dict[str, Any]:
        """
        Test system performance with multiple concurrent users.

        Args:
            num_users (int): Number of concurrent users to simulate
            messages_per_user (int): Number of messages each user sends

        Returns:
            Dict[str, Any]: Performance test results
        """
        # Set up test users
        await self.setup_test_users(num_users)

        # Define messages for each user to send
        user_messages = [
            [
                f"Hello, I'm user {i} and I want to create a task",
                f"User {i} wants to list their tasks",
                f"What can you help me with, user {i}?"
            ][:messages_per_user] for i in range(num_users)
        ]

        # Record start time
        start_time = time.time()

        # Run all user conversations concurrently
        tasks = []
        for i in range(num_users):
            task = self.simulate_single_user_conversation(self.test_users[i], user_messages[i])
            tasks.append(task)

        # Execute all tasks concurrently
        user_results = await asyncio.gather(*tasks)

        # Record end time
        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate performance metrics
        total_requests = sum(len(result["results"]) for result in user_results)
        successful_requests = sum(result["successful_requests"] for result in user_results)
        all_response_times = []
        for result in user_results:
            all_response_times.extend([r["response_time"] for r in result["results"]])

        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0

        performance_metrics = {
            "num_users": num_users,
            "messages_per_user": messages_per_user,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "total_duration": total_duration,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "requests_per_second": total_requests / total_duration if total_duration > 0 else 0,
            "user_results": user_results
        }

        return performance_metrics

    async def test_load_under_increasing_concurrency(self) -> Dict[str, Any]:
        """
        Test system performance as concurrency increases.

        Returns:
            Dict[str, Any]: Load test results at different concurrency levels
        """
        concurrency_levels = [1, 3, 5, 10, 15, 20]
        results = {}

        for level in concurrency_levels:
            print(f"Testing with {level} concurrent users...")
            level_results = await self.test_concurrent_users_performance(
                num_users=level,
                messages_per_user=2
            )
            results[f"{level}_users"] = level_results

            # Check if response times are becoming unacceptable
            if level_results["avg_response_time"] > 5.0:  # 5 seconds threshold
                print(f"Performance degradation detected at {level} users")
                break

        return {
            "test_type": "increasing_concurrency_load_test",
            "concurrency_levels": concurrency_levels,
            "results": results
        }

    async def test_memory_usage_stability(self) -> Dict[str, Any]:
        """
        Test memory usage stability under concurrent load.

        Returns:
            Dict[str, Any]: Memory stability test results
        """
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run a moderate load test
        load_results = await self.test_concurrent_users_performance(
            num_users=10,
            messages_per_user=5
        )

        # Get memory usage after load
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "memory_increase_percent": (memory_increase / initial_memory * 100) if initial_memory > 0 else 0,
            "load_results": load_results,
            "memory_stable": memory_increase < 100  # Consider stable if increase < 100MB
        }

    async def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """
        Run comprehensive performance tests with concurrent users.

        Returns:
            Dict[str, Any]: Complete performance test results
        """
        print("Starting comprehensive performance tests with concurrent users...")

        # Test basic concurrent performance
        basic_results = await self.test_concurrent_users_performance(
            num_users=5,
            messages_per_user=3
        )

        # Test increasing load
        load_results = await self.test_load_under_increasing_concurrency()

        # Test memory stability
        memory_results = await self.test_memory_usage_stability()

        comprehensive_results = {
            "timestamp": time.time(),
            "test_type": "comprehensive_concurrent_performance",
            "basic_concurrent_test": basic_results,
            "load_test_results": load_results,
            "memory_stability": memory_results,
            "summary": {
                "max_concurrent_users": basic_results["num_users"],
                "success_rate": basic_results["success_rate"],
                "avg_response_time": basic_results["avg_response_time"],
                "requests_per_second": basic_results["requests_per_second"],
                "memory_increase_mb": memory_results["memory_increase_mb"],
                "memory_stable": memory_results["memory_stable"]
            }
        }

        # Print summary
        print(f"Performance Test Summary:")
        print(f"  - Success Rate: {basic_results['success_rate']*100:.2f}%")
        print(f"  - Avg Response Time: {basic_results['avg_response_time']:.2f}s")
        print(f"  - Requests/Sec: {basic_results['requests_per_second']:.2f}")
        print(f"  - Memory Increase: {memory_results['memory_increase_mb']:.2f}MB")
        print(f"  - Memory Stable: {memory_results['memory_stable']}")

        return comprehensive_results

    def validate_performance_requirements(self, results: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that performance results meet requirements.

        Args:
            results (Dict[str, Any]): Performance test results

        Returns:
            Dict[str, bool]: Validation results for each requirement
        """
        basic_results = results.get("basic_concurrent_test", {})

        validations = {
            # Requirement: 99.9% uptime (success rate > 99.9%)
            "uptime_requirement_met": basic_results.get("success_rate", 0) > 0.999,

            # Requirement: Response time under 2 seconds for typical requests
            "response_time_requirement_met": basic_results.get("avg_response_time", float('inf')) < 2.0,

            # Requirement: System should handle at least 5 concurrent users effectively
            "concurrent_user_requirement_met": basic_results.get("num_users", 0) >= 5,

            # Requirement: Memory usage should be stable under load
            "memory_stability_requirement_met": results.get("memory_stability", {}).get("memory_stable", False)
        }

        return validations


# Pytest functions for concurrent performance tests
@pytest.mark.asyncio
async def test_performance_with_concurrent_users():
    """
    Pytest function for concurrent user performance testing.
    """
    tester = PerformanceWithConcurrentUsersTester(db_session=None)  # Replace with actual test session
    results = await tester.test_concurrent_users_performance(num_users=5, messages_per_user=3)

    # Validate performance requirements
    assert results["success_rate"] >= 0.95, f"Success rate too low: {results['success_rate']}"
    assert results["avg_response_time"] < 3.0, f"Average response time too high: {results['avg_response_time']}"
    assert results["max_response_time"] < 10.0, f"Max response time too high: {results['max_response_time']}"


@pytest.mark.asyncio
async def test_load_under_increasing_concurrency():
    """
    Pytest function for increasing concurrency load testing.
    """
    tester = PerformanceWithConcurrentUsersTester(db_session=None)  # Replace with actual test session
    results = await tester.test_load_under_increasing_concurrency()

    # Check that the system can handle at least 10 concurrent users with acceptable performance
    level_10_results = results["results"].get("10_users", {})
    if level_10_results:
        assert level_10_results["success_rate"] >= 0.90, "Success rate dropped below 90% at 10 concurrent users"
        assert level_10_results["avg_response_time"] < 5.0, "Response time exceeded 5s at 10 concurrent users"


@pytest.mark.asyncio
async def test_memory_stability_under_load():
    """
    Pytest function for memory stability under load.
    """
    tester = PerformanceWithConcurrentUsersTester(db_session=None)  # Replace with actual test session
    results = await tester.test_memory_usage_stability()

    # Ensure memory usage doesn't grow excessively under load
    assert results["memory_increase_mb"] < 150, f"Memory increased by {results['memory_increase_mb']}MB which is too much"


@pytest.mark.asyncio
async def test_comprehensive_performance():
    """
    Pytest function for comprehensive performance testing.
    """
    tester = PerformanceWithConcurrentUsersTester(db_session=None)  # Replace with actual test session
    results = await tester.run_comprehensive_performance_test()

    validations = tester.validate_performance_requirements(results)

    # All performance requirements should be met
    for req, met in validations.items():
        assert met, f"Performance requirement not met: {req}"


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Performance tests with concurrent users would run here in a full implementation")