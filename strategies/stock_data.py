"""
Stock market data utilities using yfinance

Provides functions for fetching real-time and pre-market stock data.

Phase 3 Enhancements:
- Rate limiting to prevent "Too Many Requests" errors
- Caching with 5-minute TTL to reduce API calls
- API call monitoring for health metrics
"""
import yfinance as yf
import logging
import requests
from typing import Dict, List, Optional
from decimal import Decimal
from time import time
from datetime import datetime
from zoneinfo import ZoneInfo

# Phase 3: Import infrastructure utilities
from .rate_limiter import yfinance_limiter
from .cache_utils import cached
from .api_monitoring import yfinance_monitor

logger = logging.getLogger(__name__)


def is_market_hours() -> bool:
    """
    Check if US stock market is currently open (9:30 AM - 4:00 PM ET).

    Uses ET timezone to ensure accurate detection regardless of server location.
    Excludes weekends.

    Returns:
        True if market is open, False otherwise
    """
    now_et = datetime.now(ZoneInfo('America/New_York'))

    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now_et <= market_close


def is_pre_market_hours() -> bool:
    """
    Check if US stock market is in pre-market session (4:00 AM - 9:30 AM ET).

    Uses ET timezone to ensure accurate detection regardless of server location.
    Excludes weekends.

    Returns:
        True if in pre-market session, False otherwise
    """
    now_et = datetime.now(ZoneInfo('America/New_York'))

    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Pre-market hours: 4:00 AM - 9:30 AM ET
    pre_market_start = now_et.replace(hour=4, minute=0, second=0, microsecond=0)
    pre_market_end = now_et.replace(hour=9, minute=30, second=0, microsecond=0)

    return pre_market_start <= now_et < pre_market_end


def is_after_hours() -> bool:
    """
    Check if US stock market is in after-hours session (4:00 PM - 8:00 PM ET).

    Uses ET timezone to ensure accurate detection regardless of server location.
    Excludes weekends.

    Returns:
        True if in after-hours session, False otherwise
    """
    now_et = datetime.now(ZoneInfo('America/New_York'))

    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # After-hours: 4:00 PM - 8:00 PM ET
    after_hours_start = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    after_hours_end = now_et.replace(hour=20, minute=0, second=0, microsecond=0)

    return after_hours_start <= now_et <= after_hours_end


class StockData:
    """Stock market data for a single symbol"""
    def __init__(self, symbol: str, data: Dict):
        self.symbol = symbol
        self.company_name = data.get('longName', '')
        self.current_price = data.get('currentPrice') or data.get('regularMarketPrice')
        self.previous_close = data.get('previousClose')
        self.pre_market_price = data.get('preMarketPrice')
        self.pre_market_change_percent = data.get('preMarketChangePercent')
        self.regular_market_volume = data.get('regularMarketVolume', 0)
        self.pre_market_volume = data.get('preMarketVolume', 0)
        self.market_cap = data.get('marketCap')

        # Phase 1: Volume Metrics
        self.average_volume = data.get('averageVolume')  # yfinance 3-month average volume
        self.bid = data.get('bid')
        self.ask = data.get('ask')

    @property
    def has_pre_market_data(self) -> bool:
        """Check if stock has pre-market data available"""
        return self.pre_market_price is not None

    @property
    def change_percent(self) -> Optional[float]:
        """Calculate percentage change from previous close"""
        if self.pre_market_price and self.previous_close:
            return ((self.pre_market_price - self.previous_close) / self.previous_close) * 100
        elif self.current_price and self.previous_close:
            return ((self.current_price - self.previous_close) / self.previous_close) * 100
        return None

    @property
    def display_price(self) -> Optional[float]:
        """Get the most relevant price (pre-market if available, else current)"""
        return self.pre_market_price or self.current_price

    @property
    def relative_volume_ratio(self) -> Optional[float]:
        """
        Calculate RVOL: Current volume / Average volume
        >3.0 indicates strong conviction, <1.0 indicates weak interest
        """
        if self.average_volume and self.average_volume > 0:
            current_vol = self.pre_market_volume if self.pre_market_volume > 0 else self.regular_market_volume
            if current_vol > 0:
                return current_vol / self.average_volume
        return None

    @property
    def spread_percent(self) -> Optional[float]:
        """
        Calculate bid-ask spread as percentage of mid-price
        <1% is good liquidity, >2% may indicate illiquid stock
        """
        if self.bid and self.ask and self.bid > 0:
            mid_price = (self.bid + self.ask) / 2
            if mid_price > 0:
                spread = self.ask - self.bid
                return (spread / mid_price) * 100
        return None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'current_price': self.display_price,
            'previous_close': self.previous_close,
            'change_percent': round(self.change_percent, 2) if self.change_percent else None,
            'volume': self.pre_market_volume or self.regular_market_volume,
            'market_cap': self.market_cap,
            'has_pre_market': self.has_pre_market_data,
            # Phase 1: Volume Metrics
            'pre_market_volume': self.pre_market_volume,
            'average_volume': self.average_volume,
            'relative_volume_ratio': round(self.relative_volume_ratio, 2) if self.relative_volume_ratio else None,
            'spread_percent': round(self.spread_percent, 3) if self.spread_percent else None,
        }


@yfinance_limiter
@cached(ttl_seconds=300, key_prefix='stock_info')
def _fetch_ticker_info(symbol: str) -> Dict:
    """
    Fetch ticker info with rate limiting, caching, and monitoring.

    This is an internal helper that wraps the yfinance API call
    with all Phase 3 infrastructure (rate limiting, caching, monitoring).

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict of ticker info from yfinance

    Raises:
        Exception: If API call fails after monitoring
    """
    start_time = time()

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Calculate latency
        latency_ms = int((time() - start_time) * 1000)

        # Record successful call
        yfinance_monitor.record_call(
            success=True,
            response_code=200,
            latency_ms=latency_ms
        )

        return info

    except requests.exceptions.HTTPError as e:
        # HTTP errors (429, 404, 500, etc.)
        response_code = e.response.status_code if hasattr(e, 'response') else None
        latency_ms = int((time() - start_time) * 1000)

        yfinance_monitor.record_call(
            success=False,
            response_code=response_code,
            latency_ms=latency_ms
        )

        if response_code == 429:
            logger.warning(
                f"Rate limited for {symbol}. Consider increasing cache TTL or "
                f"reducing scan frequency."
            )

        raise

    except Exception as e:
        # Other errors (network, timeout, etc.)
        latency_ms = int((time() - start_time) * 1000)

        yfinance_monitor.record_call(
            success=False,
            response_code=None,
            latency_ms=latency_ms
        )

        raise


def get_stock_data(symbols: List[str]) -> List[StockData]:
    """
    Fetch stock data for multiple symbols with rate limiting and caching.

    Phase 3: Now includes:
    - Rate limiting (5 calls/second) to prevent 429 errors
    - Caching (5-minute TTL) to reduce redundant API calls
    - API monitoring for health metrics

    Args:
        symbols: List of stock ticker symbols

    Returns:
        List of StockData objects with current and pre-market data
    """
    if not symbols:
        return []

    results = []

    for symbol in symbols:
        try:
            # Fetch ticker info (rate limited, cached, monitored)
            info = _fetch_ticker_info(symbol)

            if info and 'symbol' in info:
                stock_data = StockData(symbol, info)
                results.append(stock_data)
            else:
                logger.warning(f"No data found for symbol: {symbol}")

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            continue

    return results


def get_top_movers(symbols: List[str], limit: int = 10) -> List[StockData]:
    """
    Get stocks with biggest percentage moves (pre-market or regular)

    Args:
        symbols: List of stock ticker symbols to check
        limit: Maximum number of results to return

    Returns:
        List of StockData objects sorted by absolute % change (descending)
    """
    stocks = get_stock_data(symbols)

    # Filter out stocks without price changes
    stocks_with_changes = [s for s in stocks if s.change_percent is not None]

    # Sort by absolute percentage change (biggest movers first)
    stocks_with_changes.sort(key=lambda x: abs(x.change_percent), reverse=True)

    return stocks_with_changes[:limit]


def get_pre_market_movers(symbols: List[str], min_percent: float = 3.0, limit: int = 20) -> List[StockData]:
    """
    Get stocks with significant pre-market movement

    Args:
        symbols: List of stock ticker symbols to check
        min_percent: Minimum percentage change to include (absolute value)
        limit: Maximum number of results to return

    Returns:
        List of StockData objects with pre-market data, sorted by % change
    """
    stocks = get_stock_data(symbols)

    # Filter: must have pre-market data AND meet minimum % change
    pre_market_stocks = [
        s for s in stocks
        if s.has_pre_market_data and
        s.change_percent is not None and
        abs(s.change_percent) >= min_percent
    ]

    # Sort by absolute percentage change (biggest movers first)
    pre_market_stocks.sort(key=lambda x: abs(x.change_percent), reverse=True)

    return pre_market_stocks[:limit]


def format_price(price: Optional[float]) -> str:
    """Format price for display"""
    if price is None:
        return "N/A"
    return f"${price:.2f}"


def format_percent(percent: Optional[float]) -> str:
    """Format percentage for display with +/- sign"""
    if percent is None:
        return "N/A"
    sign = "+" if percent > 0 else ""
    return f"{sign}{percent:.2f}%"


def format_volume(volume: Optional[int]) -> str:
    """Format volume with K/M/B suffixes"""
    if volume is None or volume == 0:
        return "N/A"

    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return str(volume)
