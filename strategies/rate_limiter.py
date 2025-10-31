"""
Rate limiting for external API calls (YFinance, Finnhub, etc.)

Provides two implementations:
- RateLimiter: In-memory token bucket (dev/single-process)
- RedisRateLimiter: Redis-backed sliding window (production/multi-process)

Usage:
    from strategies.rate_limiter import yfinance_limiter

    @yfinance_limiter
    def get_stock_data(symbol):
        return yf.Ticker(symbol).info
"""

from functools import wraps
from time import sleep, time
from threading import Lock
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Thread-safe in-memory rate limiter using token bucket algorithm.

    Suitable for development and single-process environments.
    Uses a token bucket to allow burst requests up to the limit.

    Args:
        calls_per_second: Maximum number of calls per second (default 5)
    """

    def __init__(self, calls_per_second=5):
        self.rate = calls_per_second
        self.tokens = calls_per_second
        self.last_update = time()
        self.lock = Lock()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
                self.last_update = now

                # Wait if no tokens available
                if self.tokens < 1:
                    wait_time = (1 - self.tokens) / self.rate
                    logger.debug(f"Rate limit: waiting {wait_time:.2f}s for {func.__name__}")
                    sleep(wait_time)
                    self.tokens = 0
                else:
                    self.tokens -= 1

            return func(*args, **kwargs)
        return wrapper


class RedisRateLimiter:
    """
    Redis-backed rate limiter using sliding window counter algorithm.

    Coordinates rate limiting across multiple processes/workers/machines.
    Suitable for production deployments with Gunicorn/multiple workers.

    Args:
        calls_per_second: Maximum number of calls per second (default 5)
        window_seconds: Time window for rate limiting (default 1)
    """

    def __init__(self, calls_per_second=5, window_seconds=1):
        self.calls_per_second = calls_per_second
        self.window_seconds = window_seconds

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"rate_limit:{func.__name__}"
            now = time()

            try:
                # Get current call history from Redis
                cache_data = cache.get(key, {'calls': [], 'last_check': now})

                # Remove calls outside the sliding window
                cache_data['calls'] = [
                    call_time for call_time in cache_data['calls']
                    if now - call_time < self.window_seconds
                ]

                # Check if we've exceeded the rate limit
                if len(cache_data['calls']) >= self.calls_per_second:
                    oldest_call = min(cache_data['calls'])
                    sleep_time = self.window_seconds - (now - oldest_call)

                    if sleep_time > 0:
                        logger.debug(
                            f"Rate limit (Redis): waiting {sleep_time:.2f}s for {func.__name__}"
                        )
                        sleep(sleep_time)
                        now = time()
                        # Reset window after sleep
                        cache_data['calls'] = []

                # Record this call
                cache_data['calls'].append(now)
                cache_data['last_check'] = now

                # Save to Redis with TTL for auto-cleanup
                cache.set(key, cache_data, timeout=self.window_seconds * 2)

            except Exception as e:
                # If Redis fails, log warning but don't block the call
                logger.warning(
                    f"Rate limiter cache error for {func.__name__}: {e}. "
                    f"Proceeding without rate limiting."
                )

            return func(*args, **kwargs)
        return wrapper


def _get_rate_limiter_class():
    """
    Determine which rate limiter to use based on environment.

    Returns:
        RateLimiter (in-memory) for dev, RedisRateLimiter for production
    """
    # Check if Redis is available and we're not in DEBUG mode
    if settings.DEBUG:
        logger.info("Using in-memory RateLimiter (DEBUG=True)")
        return RateLimiter

    # Test Redis connectivity
    try:
        cache.set('_rate_limiter_test', 'test', timeout=1)
        if cache.get('_rate_limiter_test') == 'test':
            logger.info("Using RedisRateLimiter (production mode)")
            cache.delete('_rate_limiter_test')
            return RedisRateLimiter
    except Exception as e:
        logger.warning(
            f"Redis not available ({e}). Falling back to in-memory RateLimiter"
        )

    return RateLimiter


# Global rate limiter instances
# These are automatically configured based on environment

RateLimiterClass = _get_rate_limiter_class()

# YFinance rate limiter (5 calls/second)
yfinance_limiter = RateLimiterClass(calls_per_second=5)

# Finnhub rate limiter (60 calls/minute = 1 call/second)
finnhub_limiter = RateLimiterClass(calls_per_second=1)

logger.info(
    f"Rate limiters initialized: {RateLimiterClass.__name__} "
    f"(yfinance: 5/s, finnhub: 1/s)"
)
