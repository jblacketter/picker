"""
Unit tests for api_monitoring.py

Tests the ApiCallMonitor class for tracking API health metrics and
detecting rate limiting issues.
"""

from django.test import TestCase
from django.core.cache import cache
import unittest

from strategies.api_monitoring import (
    ApiCallMonitor,
    get_all_api_stats,
    reset_all_stats
)


class ApiCallMonitorTestCase(TestCase):
    """Tests for ApiCallMonitor basic functionality"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.monitor = ApiCallMonitor('test_api', rate_limit_threshold=0.1)

    def test_record_successful_call(self):
        """Test recording successful API call"""

        self.monitor.record_call(success=True, response_code=200, latency_ms=100)

        stats = self.monitor.get_stats()
        self.assertEqual(stats['total_calls'], 1)
        self.assertEqual(stats['successful_calls'], 1)
        self.assertEqual(stats['failed_calls'], 0)
        self.assertEqual(stats['success_rate'], 1.0)

    def test_record_failed_call(self):
        """Test recording failed API call"""

        self.monitor.record_call(success=False, response_code=500, latency_ms=200)

        stats = self.monitor.get_stats()
        self.assertEqual(stats['total_calls'], 1)
        self.assertEqual(stats['successful_calls'], 0)
        self.assertEqual(stats['failed_calls'], 1)
        self.assertEqual(stats['success_rate'], 0.0)

    def test_record_rate_limited_call(self):
        """Test recording rate limited call (429)"""

        self.monitor.record_call(success=False, response_code=429, latency_ms=50)

        stats = self.monitor.get_stats()
        self.assertEqual(stats['total_calls'], 1)
        self.assertEqual(stats['rate_limited_calls'], 1)
        self.assertEqual(stats['failed_calls'], 1)

    def test_multiple_calls_statistics(self):
        """Test that statistics are aggregated correctly"""

        # Record 10 successful calls
        for i in range(10):
            self.monitor.record_call(success=True, response_code=200, latency_ms=100 + i*10)

        # Record 2 failed calls
        self.monitor.record_call(success=False, response_code=500, latency_ms=200)
        self.monitor.record_call(success=False, response_code=404, latency_ms=50)

        # Record 1 rate limited call
        self.monitor.record_call(success=False, response_code=429, latency_ms=30)

        stats = self.monitor.get_stats()

        self.assertEqual(stats['total_calls'], 13)
        self.assertEqual(stats['successful_calls'], 10)
        self.assertEqual(stats['failed_calls'], 3)
        self.assertEqual(stats['rate_limited_calls'], 1)

        # Success rate should be 10/13 ≈ 0.769
        self.assertAlmostEqual(stats['success_rate'], 10/13, places=2)

        # Rate limited percentage should be 1/13 ≈ 0.077
        self.assertAlmostEqual(stats['rate_limited_percentage'], 1/13, places=2)

    def test_latency_tracking(self):
        """Test that latency is tracked correctly"""

        # Record calls with known latencies
        latencies = [100, 150, 200, 250, 300]
        for latency in latencies:
            self.monitor.record_call(success=True, response_code=200, latency_ms=latency)

        stats = self.monitor.get_stats()

        # Average should be (100+150+200+250+300)/5 = 200
        self.assertEqual(stats['average_latency_ms'], 200.0)


class RateLimitDetectionTestCase(TestCase):
    """Tests for rate limit threshold detection"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()

    def test_rate_limit_alert_triggered(self):
        """Test that rate limit alert is triggered when threshold exceeded"""

        # Set 10% threshold
        monitor = ApiCallMonitor('test_api', rate_limit_threshold=0.10)

        # Record 8 successful calls
        for i in range(8):
            monitor.record_call(success=True, response_code=200)

        # Record 2 rate limited calls (20% rate limited)
        monitor.record_call(success=False, response_code=429)
        monitor.record_call(success=False, response_code=429)

        stats = monitor.get_stats()

        # Rate limited percentage should be 2/10 = 20%
        self.assertAlmostEqual(stats['rate_limited_percentage'], 0.2, places=2)

        # Threshold is 10%, so alert should have been triggered
        # (We can't directly test the alert, but we can verify the stats)
        self.assertGreater(stats['rate_limited_percentage'], monitor.rate_limit_threshold,
            "Rate limit percentage should exceed threshold")

    def test_rate_limit_alert_not_triggered(self):
        """Test that alert is not triggered when below threshold"""

        # Set 10% threshold
        monitor = ApiCallMonitor('test_api', rate_limit_threshold=0.10)

        # Record 95 successful calls
        for i in range(95):
            monitor.record_call(success=True, response_code=200)

        # Record 5 rate limited calls (5% rate limited)
        for i in range(5):
            monitor.record_call(success=False, response_code=429)

        stats = monitor.get_stats()

        # Rate limited percentage should be 5/100 = 5%
        self.assertAlmostEqual(stats['rate_limited_percentage'], 0.05, places=2)

        # Below threshold, so no alert
        self.assertLess(stats['rate_limited_percentage'], monitor.rate_limit_threshold,
            "Rate limit percentage should be below threshold")

    def test_custom_threshold(self):
        """Test that custom thresholds work correctly"""

        # Very sensitive threshold (1%)
        sensitive_monitor = ApiCallMonitor('test_api', rate_limit_threshold=0.01)

        # Record 99 successful, 1 rate limited (1% rate limited)
        for i in range(99):
            sensitive_monitor.record_call(success=True, response_code=200)

        sensitive_monitor.record_call(success=False, response_code=429)

        stats = sensitive_monitor.get_stats()

        # Should be exactly at threshold (1%)
        self.assertAlmostEqual(stats['rate_limited_percentage'], 0.01, places=2)


class ApiMonitorIsolationTestCase(TestCase):
    """Tests that monitors for different APIs are isolated"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.yfinance_monitor = ApiCallMonitor('yfinance')
        self.finnhub_monitor = ApiCallMonitor('finnhub')

    def test_monitors_isolated(self):
        """Test that different API monitors don't interfere"""

        # Record calls to yfinance
        for i in range(5):
            self.yfinance_monitor.record_call(success=True, response_code=200)

        # Record calls to finnhub
        for i in range(3):
            self.finnhub_monitor.record_call(success=True, response_code=200)

        # Check stats are isolated
        yf_stats = self.yfinance_monitor.get_stats()
        fh_stats = self.finnhub_monitor.get_stats()

        self.assertEqual(yf_stats['total_calls'], 5)
        self.assertEqual(fh_stats['total_calls'], 3)

        self.assertEqual(yf_stats['api_name'], 'yfinance')
        self.assertEqual(fh_stats['api_name'], 'finnhub')


class StatsResetTestCase(TestCase):
    """Tests for resetting statistics"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.monitor = ApiCallMonitor('test_api')

    def test_reset_clears_stats(self):
        """Test that reset_stats clears all statistics"""

        # Record some calls
        for i in range(10):
            self.monitor.record_call(success=True, response_code=200, latency_ms=100)

        # Verify stats exist
        stats_before = self.monitor.get_stats()
        self.assertEqual(stats_before['total_calls'], 10)

        # Reset stats
        self.monitor.reset_stats()

        # Verify stats are cleared
        stats_after = self.monitor.get_stats()
        self.assertEqual(stats_after['total_calls'], 0)
        self.assertEqual(stats_after['successful_calls'], 0)
        self.assertEqual(stats_after['failed_calls'], 0)


class GlobalHelperFunctionsTestCase(TestCase):
    """Tests for global helper functions"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()

    def test_get_all_api_stats(self):
        """Test that get_all_api_stats returns stats for all monitors"""

        # Create monitors and record some calls
        yf_monitor = ApiCallMonitor('yfinance')
        fh_monitor = ApiCallMonitor('finnhub')

        yf_monitor.record_call(success=True, response_code=200)
        yf_monitor.record_call(success=True, response_code=200)

        fh_monitor.record_call(success=True, response_code=200)
        fh_monitor.record_call(success=False, response_code=429)

        # Get all stats
        all_stats = get_all_api_stats()

        # Should return dict with both APIs
        self.assertIsInstance(all_stats, dict)
        self.assertIn('yfinance', all_stats)
        self.assertIn('finnhub', all_stats)

        # Verify stats are correct
        self.assertEqual(all_stats['yfinance']['total_calls'], 2)
        self.assertEqual(all_stats['finnhub']['total_calls'], 2)
        self.assertEqual(all_stats['finnhub']['rate_limited_calls'], 1)

    def test_reset_all_stats(self):
        """Test that reset_all_stats clears all monitors"""

        # Create monitors and record calls
        yf_monitor = ApiCallMonitor('yfinance')
        fh_monitor = ApiCallMonitor('finnhub')

        yf_monitor.record_call(success=True, response_code=200)
        fh_monitor.record_call(success=True, response_code=200)

        # Verify stats exist
        all_stats_before = get_all_api_stats()
        self.assertGreater(len(all_stats_before), 0)

        # Reset all stats
        reset_all_stats()

        # Verify all stats are cleared
        all_stats_after = get_all_api_stats()
        for api_name, stats in all_stats_after.items():
            self.assertEqual(stats['total_calls'], 0,
                f"{api_name} stats should be cleared")


class EdgeCasesTestCase(TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.monitor = ApiCallMonitor('test_api')

    def test_zero_calls_stats(self):
        """Test that stats work with zero calls"""

        stats = self.monitor.get_stats()

        self.assertEqual(stats['total_calls'], 0)
        self.assertEqual(stats['successful_calls'], 0)
        self.assertEqual(stats['failed_calls'], 0)
        self.assertEqual(stats['success_rate'], 0.0)
        self.assertEqual(stats['average_latency_ms'], 0.0)

    def test_missing_response_code(self):
        """Test recording call without response code"""

        # Should not crash
        self.monitor.record_call(success=False, response_code=None, latency_ms=100)

        stats = self.monitor.get_stats()
        self.assertEqual(stats['total_calls'], 1)
        self.assertEqual(stats['failed_calls'], 1)

    def test_missing_latency(self):
        """Test recording call without latency"""

        # Should not crash
        self.monitor.record_call(success=True, response_code=200, latency_ms=None)

        stats = self.monitor.get_stats()
        self.assertEqual(stats['total_calls'], 1)
        # Average latency should handle None gracefully

    def test_window_configuration(self):
        """Test that custom window size works"""

        # 1-minute window
        short_monitor = ApiCallMonitor('test_api', window_minutes=1)

        short_monitor.record_call(success=True, response_code=200)

        stats = short_monitor.get_stats()
        self.assertEqual(stats['window_minutes'], 1)
        self.assertEqual(stats['total_calls'], 1)


if __name__ == '__main__':
    unittest.main()
