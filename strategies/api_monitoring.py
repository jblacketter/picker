"""
API call monitoring and rate limit detection.

Tracks API call success/failure rates to detect rate limiting issues
and provide health metrics for operational monitoring.

Usage:
    from strategies.api_monitoring import yfinance_monitor

    try:
        data = yf.Ticker('AAPL').info
        yfinance_monitor.record_call(success=True)
    except requests.exceptions.HTTPError as e:
        yfinance_monitor.record_call(
            success=False,
            response_code=e.response.status_code
        )
"""

from django.core.cache import cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ApiCallMonitor:
    """
    Monitor API call rates and detect rate limiting issues.

    Tracks call success/failure rates over a sliding window and
    triggers alerts when rate limiting threshold is exceeded.

    Args:
        api_name: Name of the API (e.g., 'yfinance', 'finnhub')
        rate_limit_threshold: Percentage of 429 errors to trigger alert (default 0.05 = 5%)
        window_minutes: Time window for tracking calls (default 5 minutes)
    """

    def __init__(self, api_name, rate_limit_threshold=0.05, window_minutes=5):
        self.api_name = api_name
        self.rate_limit_threshold = rate_limit_threshold
        self.window_minutes = window_minutes
        self._alert_cooldown_seconds = 300  # 5 minutes between alerts

    def record_call(self, success=True, response_code=None, latency_ms=None):
        """
        Record an API call outcome.

        Args:
            success: Whether the call succeeded (default True)
            response_code: HTTP response code (e.g., 200, 429, 500)
            latency_ms: Response time in milliseconds (optional)

        Example:
            monitor.record_call(success=True, response_code=200, latency_ms=150)
            monitor.record_call(success=False, response_code=429)
        """
        key = f"api_monitor:{self.api_name}:calls"

        try:
            # Get current stats from cache
            stats = cache.get(key, self._get_empty_stats())

            # Update counters
            stats['total'] += 1
            if not success:
                stats['failed'] += 1
            if response_code == 429:
                stats['rate_limited'] += 1
            if latency_ms is not None:
                stats['latencies'].append(latency_ms)
                # Keep only last 100 latencies for average calculation
                stats['latencies'] = stats['latencies'][-100:]

            # Store updated stats (TTL = window in seconds)
            cache.set(key, stats, timeout=self.window_minutes * 60)

            # Check if we need to trigger an alert
            self._check_rate_limit_threshold(stats)

        except Exception as e:
            logger.error(f"Failed to record API call for {self.api_name}: {e}")

    def _get_empty_stats(self):
        """Initialize empty statistics structure."""
        return {
            'total': 0,
            'failed': 0,
            'rate_limited': 0,
            'latencies': [],
            'start_time': datetime.now().isoformat(),
        }

    def _check_rate_limit_threshold(self, stats):
        """
        Check if rate limiting threshold is exceeded and trigger alert.

        Args:
            stats: Current API call statistics
        """
        # Need minimum sample size before checking
        if stats['total'] < 20:
            return

        rate_limited_pct = stats['rate_limited'] / stats['total']

        if rate_limited_pct > self.rate_limit_threshold:
            # Check if we're in alert cooldown
            cooldown_key = f"api_monitor:{self.api_name}:alert_cooldown"
            if cache.get(cooldown_key):
                return  # Skip alert, still in cooldown

            # Trigger alert
            logger.warning(
                f"⚠️  {self.api_name.upper()} RATE LIMIT ALERT\n"
                f"   Rate limited calls: {stats['rate_limited']}/{stats['total']} "
                f"({rate_limited_pct:.1%})\n"
                f"   Threshold: {self.rate_limit_threshold:.1%}\n"
                f"   Action: Consider increasing cache TTL or switching APIs"
            )

            # Set cooldown to prevent alert spam
            cache.set(cooldown_key, True, timeout=self._alert_cooldown_seconds)

            # Call alert handler
            self._handle_rate_limit_exceeded(stats)

    def _handle_rate_limit_exceeded(self, stats):
        """
        Handle rate limit threshold being exceeded.

        Override this method to implement custom alert handling
        (e.g., send email, Slack notification, switch to backup API).

        Args:
            stats: Current API call statistics
        """
        # Default behavior: just log the error
        logger.error(
            f"🚨 {self.api_name.upper()} experiencing rate limiting. "
            f"Stats: {stats['rate_limited']} rate limited out of {stats['total']} calls."
        )

        # Future enhancements:
        # - Send email/Slack alert
        # - Automatically increase cache TTL
        # - Switch to backup API
        # - Reduce scan frequency

    def get_stats(self):
        """
        Get current API usage statistics.

        Returns:
            Dict with call statistics for the current window

        Example:
            >>> stats = yfinance_monitor.get_stats()
            >>> print(f"Success rate: {stats['success_rate']:.1%}")
        """
        key = f"api_monitor:{self.api_name}:calls"
        stats = cache.get(key, self._get_empty_stats())

        # Calculate derived metrics
        success_count = stats['total'] - stats['failed']
        success_rate = success_count / stats['total'] if stats['total'] > 0 else 0.0
        rate_limited_pct = (
            stats['rate_limited'] / stats['total'] if stats['total'] > 0 else 0.0
        )

        # Calculate average latency
        avg_latency = (
            sum(stats['latencies']) / len(stats['latencies'])
            if stats['latencies'] else 0.0
        )

        return {
            'api_name': self.api_name,
            'total_calls': stats['total'],
            'successful_calls': success_count,
            'failed_calls': stats['failed'],
            'rate_limited_calls': stats['rate_limited'],
            'success_rate': success_rate,
            'rate_limited_percentage': rate_limited_pct,
            'average_latency_ms': avg_latency,
            'window_start': stats.get('start_time'),
            'window_minutes': self.window_minutes,
        }

    def reset_stats(self):
        """
        Reset statistics for this API.

        Useful for testing or after fixing rate limit issues.
        """
        key = f"api_monitor:{self.api_name}:calls"
        cache.delete(key)
        logger.info(f"Reset statistics for {self.api_name}")


# Global monitor instances
# These track API calls across the application

yfinance_monitor = ApiCallMonitor(
    api_name='yfinance',
    rate_limit_threshold=0.05,  # Alert at 5% rate limited calls
    window_minutes=5
)

finnhub_monitor = ApiCallMonitor(
    api_name='finnhub',
    rate_limit_threshold=0.05,
    window_minutes=5
)

logger.info(
    f"API monitors initialized: {yfinance_monitor.api_name} (5% threshold), "
    f"{finnhub_monitor.api_name} (5% threshold)"
)


def get_all_api_stats():
    """
    Get statistics for all monitored APIs.

    Returns:
        Dict mapping API names to their statistics

    Example:
        >>> all_stats = get_all_api_stats()
        >>> for api, stats in all_stats.items():
        ...     print(f"{api}: {stats['success_rate']:.1%} success")
    """
    return {
        'yfinance': yfinance_monitor.get_stats(),
        'finnhub': finnhub_monitor.get_stats(),
    }


def reset_all_stats():
    """Reset statistics for all monitored APIs."""
    yfinance_monitor.reset_stats()
    finnhub_monitor.reset_stats()
    logger.info("Reset all API monitoring statistics")
