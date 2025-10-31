"""
Caching utilities for expensive API calls and computations.

Provides a decorator for caching function results with stable key generation
that handles dicts, lists, and complex objects safely.

Usage:
    from strategies.cache_utils import cached

    @cached(ttl_seconds=300, key_prefix='stock_data')
    def get_stock_data(symbol):
        return yf.Ticker(symbol).info
"""

from django.core.cache import cache
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cached(ttl_seconds=300, key_prefix=''):
    """
    Decorator for caching function results with stable key generation.

    Handles dicts, lists, and complex objects safely by serializing them
    to JSON with sorted keys for consistent hash generation.

    Args:
        ttl_seconds: Time to live in seconds (default 300 = 5 minutes)
        key_prefix: Prefix for cache key namespace (e.g., 'stock_data')

    Returns:
        Decorated function that caches results

    Example:
        @cached(ttl_seconds=60, key_prefix='market_data')
        def get_spy_price():
            return yf.Ticker('SPY').info['regularMarketPrice']

    Note:
        - Cache keys are MD5 hashes of function name + normalized args
        - If key generation fails, function executes without caching
        - Cache misses are logged at DEBUG level for monitoring
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate stable cache key
            try:
                cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            except (TypeError, ValueError) as e:
                # If key generation fails, skip caching and execute function
                logger.warning(
                    f"Cache key generation failed for {func.__name__}: {e}. "
                    f"Executing without cache."
                )
                return func(*args, **kwargs)

            # Try to get cached value
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {func.__name__} (key: {cache_key[:8]}...)")
                return cached_value

            # Cache miss - execute function
            logger.debug(f"Cache MISS: {func.__name__} (key: {cache_key[:8]}...)")
            result = func(*args, **kwargs)

            # Store result in cache
            try:
                cache.set(cache_key, result, ttl_seconds)
                logger.debug(
                    f"Cached result for {func.__name__} "
                    f"(TTL: {ttl_seconds}s, key: {cache_key[:8]}...)"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to cache result for {func.__name__}: {e}. "
                    f"Result returned but not cached."
                )

            return result

        # Add cache inspection method
        wrapper.cache_info = lambda: {
            'function': func.__name__,
            'ttl': ttl_seconds,
            'prefix': key_prefix,
        }

        return wrapper
    return decorator


def _generate_cache_key(func, args, kwargs, key_prefix):
    """
    Generate a stable cache key from function name and arguments.

    Handles complex types (dicts, lists, objects) by serializing to JSON
    with sorted keys to ensure consistent hashing.

    Args:
        func: Function being cached
        args: Positional arguments
        kwargs: Keyword arguments
        key_prefix: Prefix for namespace isolation

    Returns:
        32-character MD5 hash string

    Raises:
        TypeError: If arguments cannot be serialized
        ValueError: If arguments contain unsupported types
    """
    # Normalize positional arguments
    normalized_args = []
    for arg in args:
        if isinstance(arg, (dict, list)):
            # Serialize dicts/lists to JSON with sorted keys
            normalized_args.append(json.dumps(arg, sort_keys=True, default=str))
        elif hasattr(arg, '__dict__'):
            # Handle objects by serializing their __dict__
            try:
                normalized_args.append(json.dumps(arg.__dict__, sort_keys=True, default=str))
            except (TypeError, ValueError):
                # Fallback to string representation
                normalized_args.append(str(arg))
        else:
            # Primitives (str, int, float, bool, None) are safe
            normalized_args.append(str(arg))

    # Include kwargs in key (sorted for stability)
    if kwargs:
        normalized_args.append(json.dumps(kwargs, sort_keys=True, default=str))

    # Build cache key: prefix:function_name:arg1:arg2:...
    key_parts = [key_prefix, func.__name__] + normalized_args
    key_str = ':'.join(filter(None, key_parts))  # filter removes empty strings

    # Generate MD5 hash (32 characters, safe for cache keys)
    cache_key = hashlib.md5(key_str.encode('utf-8')).hexdigest()

    return cache_key


def clear_cache_by_prefix(prefix):
    """
    Clear all cached values with a specific prefix.

    Note: This is not supported by all cache backends (works with Redis).
    For file-based cache, this will have no effect.

    Args:
        prefix: Cache key prefix to clear

    Returns:
        Number of keys deleted (or None if not supported)

    Example:
        clear_cache_by_prefix('stock_data')  # Clear all stock data cache
    """
    try:
        # Django-redis supports delete_pattern
        if hasattr(cache, 'delete_pattern'):
            pattern = f"*{prefix}*"
            deleted = cache.delete_pattern(pattern)
            logger.info(f"Cleared {deleted} cache entries with prefix '{prefix}'")
            return deleted
        else:
            logger.warning(
                f"Cache backend does not support delete_pattern. "
                f"Cannot clear prefix '{prefix}'"
            )
            return None
    except Exception as e:
        logger.error(f"Failed to clear cache with prefix '{prefix}': {e}")
        return None


def get_cache_stats():
    """
    Get cache statistics (if supported by backend).

    Returns:
        Dict with cache statistics or None if not supported

    Example:
        stats = get_cache_stats()
        # {'hits': 1234, 'misses': 56, 'hit_rate': 0.957}
    """
    try:
        # Django-redis supports get_stats
        if hasattr(cache, 'get_stats'):
            return cache.get_stats()
        else:
            logger.debug("Cache backend does not support statistics")
            return None
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return None


# Convenience function for manual cache invalidation
def invalidate_cache(func, *args, **kwargs):
    """
    Manually invalidate cache for a specific function call.

    Args:
        func: Cached function
        *args: Same positional arguments as the cached call
        **kwargs: Same keyword arguments as the cached call

    Returns:
        True if cache was invalidated, False otherwise

    Example:
        @cached(ttl_seconds=300)
        def get_stock_data(symbol):
            return yf.Ticker(symbol).info

        # Later, force refresh:
        invalidate_cache(get_stock_data, 'AAPL')
    """
    try:
        # Get the cache key prefix from function metadata
        if hasattr(func, 'cache_info'):
            info = func.cache_info()
            key_prefix = info.get('prefix', '')
        else:
            key_prefix = ''

        # Generate the same cache key
        cache_key = _generate_cache_key(func, args, kwargs, key_prefix)

        # Delete from cache
        cache.delete(cache_key)
        logger.debug(f"Invalidated cache for {func.__name__} (key: {cache_key[:8]}...)")
        return True

    except Exception as e:
        logger.error(f"Failed to invalidate cache for {func.__name__}: {e}")
        return False
