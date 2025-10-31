"""
Market Context Service - Wave 2 Feature 2.1

Provides real-time market overview data (SPY, QQQ, VIX, futures, sentiment)
to help users understand the broader market environment when evaluating
pre-market movers.

Phase 3 Enhancements:
- Cached for 1 minute (balance freshness vs API calls)
- Rate limited via Wave 1 infrastructure
- API monitoring via yfinance_monitor
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging
import yfinance as yf

# Wave 1 infrastructure
from .cache_utils import cached
from .rate_limiter import yfinance_limiter
from .api_monitoring import yfinance_monitor
from time import time

logger = logging.getLogger(__name__)


@dataclass
class MarketContext:
    """
    Snapshot of overall market conditions.

    Used to provide context for pre-market movers - helps users understand
    if a stock is moving with or against the broader market trend.
    """
    spy_change: float          # S&P 500 change % from previous close
    qqq_change: float          # Nasdaq 100 change % from previous close
    vix_level: float           # VIX (fear index) current level
    es_futures: Optional[float]  # E-mini S&P futures change %
    nq_futures: Optional[float]  # Nasdaq futures change %
    market_sentiment: str      # 'bullish', 'neutral', 'bearish'
    last_updated: datetime

    # Raw prices for display
    spy_price: float
    qqq_price: float
    vix_price: float

    @property
    def is_risk_on(self) -> bool:
        """
        Risk-on environment: SPY up, VIX low
        Typically favorable for growth stocks and high-beta plays
        """
        return self.spy_change > 0 and self.vix_level < 20

    @property
    def is_risk_off(self) -> bool:
        """
        Risk-off environment: SPY down, VIX elevated
        Typically defensive posture, flight to safety
        """
        return self.spy_change < -0.5 and self.vix_level > 25

    @property
    def sentiment_color(self) -> str:
        """Get Tailwind color class for sentiment badge"""
        if self.market_sentiment == 'bullish':
            return 'green'
        elif self.market_sentiment == 'bearish':
            return 'red'
        else:
            return 'gray'

    @property
    def sentiment_emoji(self) -> str:
        """Get emoji for sentiment display"""
        if self.market_sentiment == 'bullish':
            return '✅'
        elif self.market_sentiment == 'bearish':
            return '⚠️'
        else:
            return '➖'

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'spy_change': round(self.spy_change, 2),
            'qqq_change': round(self.qqq_change, 2),
            'vix_level': round(self.vix_level, 2),
            'es_futures': round(self.es_futures, 2) if self.es_futures else None,
            'nq_futures': round(self.nq_futures, 2) if self.nq_futures else None,
            'market_sentiment': self.market_sentiment,
            'last_updated': self.last_updated.strftime('%I:%M %p ET'),
            'spy_price': round(self.spy_price, 2),
            'qqq_price': round(self.qqq_price, 2),
            'vix_price': round(self.vix_price, 2),
            'is_risk_on': self.is_risk_on,
            'is_risk_off': self.is_risk_off,
            'sentiment_color': self.sentiment_color,
            'sentiment_emoji': self.sentiment_emoji,
        }


@yfinance_limiter
@cached(ttl_seconds=60, key_prefix='market_context')
def get_market_context() -> Optional[MarketContext]:
    """
    Fetch current market conditions with Wave 1 infrastructure.

    Cached for 1 minute to reduce API calls while maintaining freshness.
    Rate limited and monitored for reliability.

    Returns:
        MarketContext object or None if fetch fails
    """
    start_time = time()

    try:
        # Fetch major indices
        spy = yf.Ticker('SPY').info
        qqq = yf.Ticker('QQQ').info
        vix = yf.Ticker('^VIX').info

        # Calculate percentage changes
        spy_current = spy.get('regularMarketPrice') or spy.get('currentPrice')
        spy_prev = spy.get('previousClose')
        qqq_current = qqq.get('regularMarketPrice') or qqq.get('currentPrice')
        qqq_prev = qqq.get('previousClose')
        vix_current = vix.get('regularMarketPrice') or vix.get('currentPrice')

        if not all([spy_current, spy_prev, qqq_current, qqq_prev, vix_current]):
            logger.error("Missing required market data from YFinance")
            return None

        spy_change = ((spy_current - spy_prev) / spy_prev) * 100
        qqq_change = ((qqq_current - qqq_prev) / qqq_prev) * 100

        # Fetch futures (may fail, so use try/except)
        es_futures_change = None
        nq_futures_change = None

        try:
            es = yf.Ticker('ES=F').info
            if es.get('regularMarketPrice') and es.get('previousClose'):
                es_futures_change = ((es['regularMarketPrice'] - es['previousClose']) / es['previousClose']) * 100
        except Exception as e:
            logger.warning(f"Could not fetch ES futures: {e}")

        try:
            nq = yf.Ticker('NQ=F').info
            if nq.get('regularMarketPrice') and nq.get('previousClose'):
                nq_futures_change = ((nq['regularMarketPrice'] - nq['previousClose']) / nq['previousClose']) * 100
        except Exception as e:
            logger.warning(f"Could not fetch NQ futures: {e}")

        # Determine market sentiment
        sentiment = determine_sentiment(spy_change, vix_current)

        # Record successful API call
        latency_ms = int((time() - start_time) * 1000)
        yfinance_monitor.record_call(success=True, response_code=200, latency_ms=latency_ms)

        logger.info(
            f"Market context fetched: SPY {spy_change:+.2f}%, "
            f"QQQ {qqq_change:+.2f}%, VIX {vix_current:.2f}, "
            f"Sentiment: {sentiment}"
        )

        return MarketContext(
            spy_change=spy_change,
            qqq_change=qqq_change,
            vix_level=vix_current,
            es_futures=es_futures_change,
            nq_futures=nq_futures_change,
            market_sentiment=sentiment,
            last_updated=datetime.now(),
            spy_price=spy_current,
            qqq_price=qqq_current,
            vix_price=vix_current,
        )

    except Exception as e:
        # Record failed API call
        latency_ms = int((time() - start_time) * 1000)
        yfinance_monitor.record_call(success=False, response_code=None, latency_ms=latency_ms)

        logger.error(f"Failed to fetch market context: {e}", exc_info=True)
        return None


def determine_sentiment(spy_change: float, vix_level: float) -> str:
    """
    Determine market sentiment based on SPY movement and VIX level.

    Logic:
    - Bullish: SPY up significantly (>0.5%) AND VIX low (<18)
    - Bearish: SPY down significantly (<-0.5%) OR VIX elevated (>25)
    - Neutral: Everything else

    Args:
        spy_change: S&P 500 percentage change
        vix_level: Current VIX level

    Returns:
        'bullish', 'bearish', or 'neutral'
    """
    if spy_change > 0.5 and vix_level < 18:
        return 'bullish'
    elif spy_change < -0.5 or vix_level > 25:
        return 'bearish'
    else:
        return 'neutral'


def format_percent_change(value: Optional[float]) -> str:
    """
    Format percentage change for display.

    Args:
        value: Percentage change (e.g., 1.23 for +1.23%)

    Returns:
        Formatted string with sign and % (e.g., "+1.23%")
    """
    if value is None:
        return "N/A"

    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def get_change_color_class(value: Optional[float]) -> str:
    """
    Get Tailwind color class based on positive/negative change.

    Args:
        value: Percentage change

    Returns:
        Tailwind text color class
    """
    if value is None:
        return "text-gray-500"
    elif value > 0:
        return "text-green-600 dark:text-green-400"
    elif value < 0:
        return "text-red-600 dark:text-red-400"
    else:
        return "text-gray-600 dark:text-gray-400"
