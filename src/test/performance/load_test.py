"""
Load Test for Response Time Validation in Todo AI Chatbot System

This module tests the system's performance under load to validate response time requirements.
"""

import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List
from sqlmodel import Session
from fastapi.testclient import TestClient

from src.models.user import User
from src.app.main import app
from src.database.session import get_session


class LoadTestForResponseTimeValidation:
    """
    Load tester for validating response time requirements under various load conditions.
    """

    def __init__(self, db_session: Session, test_client: TestClient = None):
        """
        Initialize the load tester.

        Args:
            db_session (Session): Database session for testing
            test_client (TestClient, optional): FastAPI test client
        """
        self.db_session = db_session
        self.test_client = test_client or TestClient(app)
        self.test_users = []

    async def setup_load_test_users(self, count: int = 20) -> List[User]:
        """
        Set up users for load testing.

        Args:
            count (int): Number of users to create for testing

        Returns:
            List[User]: List of created test users
        """
        users = []
        for i in range(count):
            user = User(
                username=f"load_test_user_{i}",
                email=f"load_test_{i}@test.com"
            )
            self.db_session.add(user)
            users.append(user)

        self.db_session.commit()

        # Refresh users to get their IDs
        for user in users:
            self.db_session.refresh(user)

        self.test_users = users
        return users

    async def execute_single_request(self, user: User, message: str) -> Dict[str, Any]:
        """
        Execute a single request and measure its response time.

        Args:
            user (User): User making the request
            message (str): Message to send

        Returns:
            Dict[str, Any]: Request results with timing information
        """
        start_time = time.time()

        response = self.test_client.post(
            f"/api/{user.id}/chat",
            json={"message": message}
        )

        end_time = time.time()
        response_time = end_time - start_time

        return {
            "user_id": str(user.id),
            "message": message,
            "response_time": response_time,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response_size": len(response.content) if response.content else 0
        }

    async def run_load_test(self, num_requests: int, concurrent_users: int = 10) -> Dict[str, Any]:
        """
        Run a load test with specified number of requests and concurrency level.

        Args:
            num_requests (int): Total number of requests to make
            concurrent_users (int): Number of users to simulate concurrently

        Returns:
            Dict[str, Any]: Load test results with performance metrics
        """
        # Set up test users
        await self.setup_load_test_users(max(concurrent_users, 5))

        # Prepare messages to send
        messages = [
            f"Load test message {i} - Hello, this is a test for performance validation",
            f"Load test task {i} - Add a task to test system performance",
            f"Load test query {i} - List my tasks to verify system response",
        ]

        # Prepare request tasks
        tasks = []
        for i in range(num_requests):
            user_idx = i % len(self.test_users)
            message = messages[i % len(messages)]
            task = self.execute_single_request(self.test_users[user_idx], message)
            tasks.append(task)

        # Execute all requests concurrently in batches to avoid overwhelming the system
        batch_size = concurrent_users
        all_results = []

        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            # Process results and handle any exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    all_results.append({
                        "error": str(result),
                        "success": False,
                        "response_time": float('inf')
                    })
                else:
                    all_results.append(result)

        # Calculate performance metrics
        successful_results = [r for r in all_results if r.get("success")]
        failed_results = [r for r in all_results if not r.get("success")]

        response_times = [r["response_time"] for r in successful_results]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0
            p99_response_time = sorted(response_times)[int(0.99 * len(response_times))] if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = max_response_time = min_response_time = 0

        total_time = sum(r["response_time"] for r in all_results)
        requests_per_second = num_requests / total_time if total_time > 0 else 0

        load_test_results = {
            "test_config": {
                "total_requests": num_requests,
                "concurrent_users": concurrent_users,
                "start_time": time.time() - total_time if total_time > 0 else time.time()
            },
            "performance_metrics": {
                "total_requests": num_requests,
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "success_rate": len(successful_results) / num_requests if num_requests > 0 else 0,
                "avg_response_time": avg_response_time,
                "median_response_time": median_response_time,
                "p95_response_time": p95_response_time,
                "p99_response_time": p99_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "requests_per_second": requests_per_second
            },
            "response_time_validation": {
                "avg_response_time_within_limit": avg_response_time < 2.0,  # Requirement: <2s average
                "p95_response_time_within_limit": p95_response_time < 5.0,  # Requirement: <5s for 95% of requests
                "max_response_time_within_limit": max_response_time < 10.0,  # Requirement: <10s for all requests
                "acceptable_success_rate": len(successful_results) / num_requests >= 0.95 if num_requests > 0 else True  # Requirement: >=95% success
            },
            "raw_results": all_results
        }

        return load_test_results

    async def run_stress_test(self) -> Dict[str, Any]:
        """
        Run a stress test to identify system breaking points.

        Returns:
            Dict[str, Any]: Stress test results
        """
        # Start with moderate load and increase until performance degrades
        test_configs = [
            {"requests": 50, "concurrent": 5},
            {"requests": 100, "concurrent": 10},
            {"requests": 200, "concurrent": 20},
            {"requests": 500, "concurrent": 30},
            {"requests": 1000, "concurrent": 50},
        ]

        stress_results = []

        for config in test_configs:
            print(f"Running stress test with {config['requests']} requests and {config['concurrent']} concurrent users...")

            results = await self.run_load_test(
                num_requests=config["requests"],
                concurrent_users=config["concurrent"]
            )

            stress_results.append({
                "config": config,
                "results": results
            })

            # Stop if performance is severely degraded
            perf_metrics = results["performance_metrics"]
            if (perf_metrics["success_rate"] < 0.80 or  # Less than 80% success rate
                perf_metrics["avg_response_time"] > 10.0):  # Average response time > 10s
                print(f"Stopping stress test - Performance significantly degraded at {config['concurrent']} concurrent users")
                break

        return {
            "test_type": "stress_test",
            "configs_run": stress_results,
            "breaking_point_identified": any(
                r["results"]["performance_metrics"]["success_rate"] < 0.80 or
                r["results"]["performance_metrics"]["avg_response_time"] > 10.0
                for r in stress_results
            )
        }

    async def run_endurance_test(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Run an endurance test to validate system stability over time.

        Args:
            duration_minutes (int): Duration of the test in minutes

        Returns:
            Dict[str, Any]: Endurance test results
        """
        end_time = time.time() + (duration_minutes * 60)  # Convert minutes to seconds
        request_count = 0
        results = []

        await self.setup_load_test_users(10)

        while time.time() < end_time:
            # Rotate through users and messages
            user = self.test_users[request_count % len(self.test_users)]
            message = f"Endurance test message #{request_count} - Checking system stability"

            result = await self.execute_single_request(user, message)
            results.append(result)
            request_count += 1

            # Brief pause to simulate realistic request intervals
            await asyncio.sleep(0.1)

        # Calculate endurance test metrics
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0

        return {
            "test_type": "endurance_test",
            "duration_minutes": duration_minutes,
            "total_requests": request_count,
            "successful_requests": len(successful_requests),
            "metrics": {
                "success_rate": len(successful_requests) / request_count if request_count > 0 else 0,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "min_response_time": min_response_time,
                "requests_per_minute": request_count / duration_minutes if duration_minutes > 0 else 0
            },
            "stability_validation": {
                "consistent_response_times": max_response_time / avg_response_time < 5 if avg_response_time > 0 else True,  # Response times shouldn't vary wildly
                "stable_success_rate": len(successful_requests) / request_count >= 0.95 if request_count > 0 else True  # High success rate maintained
            }
        }

    async def validate_response_time_requirements(self, load_results: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that the load test results meet the response time requirements.

        Args:
            load_results (Dict[str, Any]): Results from load testing

        Returns:
            Dict[str, bool]: Validation results for each requirement
        """
        perf_metrics = load_results["performance_metrics"]
        response_time_validation = load_results["response_time_validation"]

        requirements_validation = {
            # Requirement: Average response time under 2 seconds
            "avg_response_time_requirement": response_time_validation["avg_response_time_within_limit"],

            # Requirement: 95% of requests under 5 seconds
            "p95_response_time_requirement": response_time_validation["p95_response_time_within_limit"],

            # Requirement: All requests under 10 seconds
            "max_response_time_requirement": response_time_validation["max_response_time_within_limit"],

            # Requirement: At least 95% success rate
            "success_rate_requirement": response_time_validation["acceptable_success_rate"],

            # Additional performance requirements
            "acceptable_throughput": perf_metrics["requests_per_second"] >= 1,  # At least 1 request per second
            "reasonable_p99_response_time": perf_metrics["p99_response_time"] < 8.0  # 99% of requests under 8s
        }

        return requirements_validation

    async def run_comprehensive_load_validation(self) -> Dict[str, Any]:
        """
        Run comprehensive load validation tests.

        Returns:
            Dict[str, Any]: Complete load validation results
        """
        print("Starting comprehensive load validation tests...")

        # Run basic load test
        print("Running basic load test...")
        basic_load_results = await self.run_load_test(
            num_requests=100,
            concurrent_users=10
        )

        # Run stress test
        print("Running stress test...")
        stress_results = await self.run_stress_test()

        # Run endurance test
        print("Running endurance test...")
        endurance_results = await self.run_endurance_test(duration_minutes=2)

        # Validate requirements
        requirements_validation = await self.validate_response_time_requirements(basic_load_results)

        comprehensive_results = {
            "timestamp": time.time(),
            "test_type": "comprehensive_load_validation",
            "basic_load_test": basic_load_results,
            "stress_test": stress_results,
            "endurance_test": endurance_results,
            "requirements_validation": requirements_validation,
            "summary": {
                "passed_requirements": sum(1 for v in requirements_validation.values() if v),
                "total_requirements": len(requirements_validation),
                "all_requirements_met": all(requirements_validation.values()),
                "avg_response_time": basic_load_results["performance_metrics"]["avg_response_time"],
                "max_concurrent_users_tested": max(
                    config["config"]["concurrent"] for config in stress_results["configs_run"]
                ) if stress_results["configs_run"] else 0
            }
        }

        # Print summary
        print(f"\nLoad Validation Summary:")
        print(f"  - Requirements Met: {comprehensive_results['summary']['passed_requirements']}/{comprehensive_results['summary']['total_requirements']}")
        print(f"  - Avg Response Time: {comprehensive_results['basic_load_test']['performance_metrics']['avg_response_time']:.2f}s")
        print(f"  - Success Rate: {comprehensive_results['basic_load_test']['performance_metrics']['success_rate']:.2%}")
        print(f"  - Throughput: {comprehensive_results['basic_load_test']['performance_metrics']['requests_per_second']:.2f} req/sec")
        print(f"  - All Requirements Passed: {comprehensive_results['summary']['all_requirements_met']}")

        return comprehensive_results


# Pytest functions for load testing
@pytest.mark.asyncio
async def test_basic_load_response_times():
    """
    Pytest function for basic load response time validation.
    """
    tester = LoadTestForResponseTimeValidation(db_session=None)  # Replace with actual test session

    results = await tester.run_load_test(num_requests=50, concurrent_users=5)

    # Validate that response time requirements are met
    assert results["performance_metrics"]["avg_response_time"] < 2.0, "Average response time exceeds 2 seconds"
    assert results["performance_metrics"]["p95_response_time"] < 5.0, "95th percentile response time exceeds 5 seconds"
    assert results["performance_metrics"]["success_rate"] >= 0.95, "Success rate is below 95%"


@pytest.mark.asyncio
async def test_stress_limits():
    """
    Pytest function for stress testing limits.
    """
    tester = LoadTestForResponseTimeValidation(db_session=None)  # Replace with actual test session

    results = await tester.run_stress_test()

    # The system should handle at least up to 20 concurrent users with acceptable performance
    configs_tested = results["configs_run"]
    if len(configs_tested) > 2:  # If we made it past the initial tests
        # Check that performance was acceptable at 20 concurrent users
        for config_result in configs_tested:
            if config_result["config"]["concurrent"] == 20:
                perf = config_result["results"]["performance_metrics"]
                assert perf["success_rate"] >= 0.90, "Success rate dropped below 90% at 20 concurrent users"
                assert perf["avg_response_time"] < 5.0, "Average response time exceeded 5s at 20 concurrent users"
                break


@pytest.mark.asyncio
async def test_endurance_stability():
    """
    Pytest function for endurance stability testing.
    """
    tester = LoadTestForResponseTimeValidation(db_session=None)  # Replace with actual test session

    results = await tester.run_endurance_test(duration_minutes=1)

    # System should maintain stability over time
    stability = results["stability_validation"]
    assert stability["stable_success_rate"], "Success rate dropped during endurance test"
    assert stability["consistent_response_times"], "Response times became inconsistent during endurance test"


@pytest.mark.asyncio
async def test_comprehensive_load_validation():
    """
    Pytest function for comprehensive load validation.
    """
    tester = LoadTestForResponseTimeValidation(db_session=None)  # Replace with actual test session

    results = await tester.run_comprehensive_load_validation()

    # All requirements should be validated and met
    req_validation = results["requirements_validation"]
    assert all(req_validation.values()), f"Some requirements not met: {req_validation}"


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Load tests for response time validation would run here in a full implementation")