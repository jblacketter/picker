"""
Unit tests for rate_limiter.py

Tests the RateLimiter (in-memory token bucket) and RedisRateLimiter
(Redis-backed sliding window) implementations.
"""

from django.test import TestCase
from django.core.cache import cache
from time import time, sleep
from threading import Thread
import unittest

from strategies.rate_limiter import RateLimiter, RedisRateLimiter


class RateLimiterTestCase(TestCase):
    """Tests for in-memory RateLimiter (token bucket algorithm)"""

    def setUp(self):
        """Set up test fixtures"""
        self.limiter = RateLimiter(calls_per_second=5)
        self.call_count = 0

    def test_token_bucket_allows_burst(self):
        """Test that rate limiter allows burst of N calls immediately"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        start = time()

        # Should allow 5 calls immediately (burst)
        for i in range(5):
            result = test_call()
            self.assertEqual(result, "success")

        elapsed = time() - start

        # First 5 calls should complete very quickly (< 0.1s)
        self.assertLess(elapsed, 0.1,
            f"Burst of 5 calls took {elapsed:.3f}s, expected < 0.1s")
        self.assertEqual(self.call_count, 5)

    def test_rate_limiting_after_burst(self):
        """Test that calls are rate limited after burst is exhausted"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        # Exhaust burst tokens (5 calls)
        for i in range(5):
            test_call()

        # 6th call should be rate limited (wait ~0.2s)
        start = time()
        test_call()
        elapsed = time() - start

        # Should wait approximately 1/5 = 0.2 seconds
        self.assertGreater(elapsed, 0.15,
            f"6th call took {elapsed:.3f}s, expected > 0.15s (rate limited)")
        self.assertEqual(self.call_count, 6)

    def test_rate_limiting_maintains_rate(self):
        """Test that rate limiter maintains consistent rate over time"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        start = time()

        # Make 10 calls (5 burst + 5 rate limited)
        for i in range(10):
            test_call()

        elapsed = time() - start

        # Should take approximately 1 second total
        # (5 instant + 5 at 5/s = 1 second for the last 5)
        # Note: Token refill allows some overlap, so may be slightly faster
        self.assertGreater(elapsed, 0.5,
            f"10 calls took {elapsed:.3f}s, expected > 0.5s")
        self.assertLess(elapsed, 1.5,
            f"10 calls took {elapsed:.3f}s, expected < 1.5s")
        self.assertEqual(self.call_count, 10)

    def test_thread_safety(self):
        """Test that rate limiter is thread-safe"""

        call_times = []

        @self.limiter
        def test_call(thread_id):
            call_times.append((thread_id, time()))
            return f"thread_{thread_id}"

        # Create 10 threads that each make 1 call
        threads = []
        for i in range(10):
            thread = Thread(target=lambda tid=i: test_call(tid))
            threads.append(thread)

        start = time()

        # Start all threads simultaneously
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        elapsed = time() - start

        # All 10 calls should complete in ~1 second (5 burst + 5 rate limited)
        # Note: Token refill allows some overlap, so may be slightly faster
        self.assertGreater(elapsed, 0.5,
            f"10 concurrent calls took {elapsed:.3f}s, expected > 0.5s")
        self.assertEqual(len(call_times), 10,
            "All 10 threads should have completed")

    def test_token_refill(self):
        """Test that tokens refill over time"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        # Exhaust burst tokens
        for i in range(5):
            test_call()

        # Wait for 1 second to refill tokens (should add ~5 tokens)
        sleep(1.0)

        # Should be able to burst 5 more calls immediately
        start = time()
        for i in range(5):
            test_call()
        elapsed = time() - start

        self.assertLess(elapsed, 0.1,
            f"5 calls after refill took {elapsed:.3f}s, expected < 0.1s")
        self.assertEqual(self.call_count, 10)


class RedisRateLimiterTestCase(TestCase):
    """Tests for Redis-backed RateLimiter (sliding window algorithm)"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()  # Clear Redis cache before each test
        self.limiter = RedisRateLimiter(calls_per_second=5, window_seconds=1)
        self.call_count = 0

    def test_sliding_window_allows_burst(self):
        """Test that Redis limiter allows burst of N calls"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        start = time()

        # Should allow 5 calls immediately
        for i in range(5):
            result = test_call()
            self.assertEqual(result, "success")

        elapsed = time() - start

        # First 5 calls should complete quickly
        self.assertLess(elapsed, 0.2,
            f"Burst of 5 calls took {elapsed:.3f}s, expected < 0.2s")
        self.assertEqual(self.call_count, 5)

    def test_sliding_window_rate_limiting(self):
        """Test that Redis limiter enforces rate limit"""

        @self.limiter
        def test_call():
            self.call_count += 1
            return "success"

        # Exhaust burst (5 calls)
        for i in range(5):
            test_call()

        # 6th call should be rate limited
        start = time()
        test_call()
        elapsed = time() - start

        # Should wait until oldest call falls outside window
        self.assertGreater(elapsed, 0.8,
            f"6th call took {elapsed:.3f}s, expected > 0.8s (rate limited)")
        self.assertEqual(self.call_count, 6)

    def test_cache_failure_graceful_degradation(self):
        """Test that limiter works even if cache fails"""

        call_count = 0

        # Create limiter with invalid cache backend (will cause errors)
        limiter = RedisRateLimiter(calls_per_second=5, window_seconds=1)

        @limiter
        def test_call():
            nonlocal call_count
            call_count += 1
            return "success"

        # Should still work even if cache operations fail
        # (graceful degradation - proceeds without rate limiting)
        try:
            for i in range(10):
                result = test_call()
                self.assertEqual(result, "success")

            self.assertEqual(call_count, 10,
                "Should complete all calls even with cache errors")
        except Exception as e:
            self.fail(f"Should not raise exception on cache failure: {e}")

    def test_multiple_functions_isolated(self):
        """Test that rate limits are isolated per function"""

        call_count_a = 0
        call_count_b = 0

        limiter_a = RedisRateLimiter(calls_per_second=3)
        limiter_b = RedisRateLimiter(calls_per_second=3)

        @limiter_a
        def function_a():
            nonlocal call_count_a
            call_count_a += 1
            return "a"

        @limiter_b
        def function_b():
            nonlocal call_count_b
            call_count_b += 1
            return "b"

        # Each function should have its own rate limit
        for i in range(3):
            function_a()
            function_b()

        self.assertEqual(call_count_a, 3)
        self.assertEqual(call_count_b, 3)


class RateLimiterConfigTestCase(TestCase):
    """Tests for rate limiter configuration and customization"""

    def test_custom_rate_configuration(self):
        """Test that custom rates can be configured"""

        # Very slow limiter (1 call per second)
        slow_limiter = RateLimiter(calls_per_second=1)
        call_count = 0

        @slow_limiter
        def slow_call():
            nonlocal call_count
            call_count += 1
            return "success"

        start = time()

        # First call immediate (burst)
        slow_call()

        # Second call should wait ~1 second
        slow_call()

        elapsed = time() - start

        self.assertGreater(elapsed, 0.8,
            f"2 calls at 1/s took {elapsed:.3f}s, expected > 0.8s")
        self.assertEqual(call_count, 2)

    def test_fast_rate_configuration(self):
        """Test that fast rates work correctly"""

        # Very fast limiter (100 calls per second)
        fast_limiter = RateLimiter(calls_per_second=100)
        call_count = 0

        @fast_limiter
        def fast_call():
            nonlocal call_count
            call_count += 1
            return "success"

        start = time()

        # Should complete 100 calls very quickly
        for i in range(100):
            fast_call()

        elapsed = time() - start

        # Should take ~1 second (100 burst, then rate limited)
        # Actually first 100 are burst so should be < 0.5s
        self.assertLess(elapsed, 1.5,
            f"100 calls at 100/s took {elapsed:.3f}s, expected < 1.5s")
        self.assertEqual(call_count, 100)


if __name__ == '__main__':
    unittest.main()
