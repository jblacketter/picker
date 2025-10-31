"""
Finnhub API service for fetching market data and news.

Provides functions for:
- Fetching company news
- Getting market status (pre-market, regular, after-hours)
- Real-time quote data

Phase 3 Enhancements:
- Caching with 15-minute TTL for news (news doesn't change rapidly)
- API call monitoring for health metrics
"""

import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings

# Phase 3: Import infrastructure utilities
from .cache_utils import cached
from .api_monitoring import finnhub_monitor

logger = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


class FinnhubClient:
    """Client for interacting with Finnhub API."""

    def __init__(self, api_key=None):
        """Initialize with API key from settings or parameter."""
        self.api_key = api_key or settings.FINNHUB_API_KEY
        if not self.api_key:
            logger.warning("Finnhub API key not configured")

    def _make_request(self, endpoint, params=None):
        """Make a request to Finnhub API with error handling."""
        if not self.api_key:
            logger.error("Cannot make Finnhub request - API key not configured")
            return None

        if params is None:
            params = {}

        params['token'] = self.api_key
        url = f"{FINNHUB_BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Finnhub API request failed: {e}")
            return None

    @cached(ttl_seconds=900, key_prefix='finnhub_news')  # 15-minute cache
    def get_company_news(self, symbol, days_back=7):
        """
        Fetch recent company news with caching.

        Phase 3: Cached for 15 minutes (news doesn't change rapidly)

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            days_back: Number of days to look back (default 7)

        Returns:
            List of news articles with headline, summary, source, url, datetime
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        params = {
            'symbol': symbol.upper(),
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d')
        }

        # Track API call for monitoring
        try:
            data = self._make_request('company-news', params)
            finnhub_monitor.record_call(success=True, response_code=200)
        except Exception as e:
            finnhub_monitor.record_call(success=False, response_code=None)
            raise

        if not data:
            return []

        # Parse and format news articles
        articles = []
        for item in data[:10]:  # Limit to 10 most recent
            articles.append({
                'headline': item.get('headline', 'No headline'),
                'summary': item.get('summary', ''),
                'source': item.get('source', 'Unknown'),
                'url': item.get('url', ''),
                'datetime': datetime.fromtimestamp(item.get('datetime', 0)),
                'category': item.get('category', ''),
                'related': item.get('related', '')
            })

        # Sort by datetime, most recent first
        articles.sort(key=lambda x: x['datetime'], reverse=True)

        logger.info(f"Fetched {len(articles)} news articles for {symbol}")
        return articles

    def get_quote(self, symbol):
        """
        Get real-time quote for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with current price, change, percent change, etc.
        """
        params = {'symbol': symbol.upper()}
        data = self._make_request('quote', params)

        if not data:
            return None

        return {
            'current_price': data.get('c', 0),
            'change': data.get('d', 0),
            'percent_change': data.get('dp', 0),
            'high': data.get('h', 0),
            'low': data.get('l', 0),
            'open': data.get('o', 0),
            'previous_close': data.get('pc', 0),
            'timestamp': datetime.fromtimestamp(data.get('t', 0))
        }

    def get_market_status(self):
        """
        Get current market status.

        Returns:
            Dict with market state (open/closed) and session type
        """
        # Finnhub uses 'market-status' endpoint for US markets
        data = self._make_request('stock/market-status', {'exchange': 'US'})

        if not data:
            return None

        return {
            'exchange': data.get('exchange', 'US'),
            'is_open': data.get('isOpen', False),
            'session': data.get('session', 'unknown'),  # pre, regular, post, or closed
            'timezone': data.get('timezone', 'America/New_York')
        }

    def get_top_news(self, category='general', limit=10):
        """
        Get general market news.

        Args:
            category: News category (general, forex, crypto, merger)
            limit: Maximum number of articles to return

        Returns:
            List of news articles
        """
        params = {'category': category}
        data = self._make_request('news', params)

        if not data:
            return []

        articles = []
        for item in data[:limit]:
            articles.append({
                'headline': item.get('headline', 'No headline'),
                'summary': item.get('summary', ''),
                'source': item.get('source', 'Unknown'),
                'url': item.get('url', ''),
                'datetime': datetime.fromtimestamp(item.get('datetime', 0)),
                'category': item.get('category', ''),
                'image': item.get('image', '')
            })

        return articles


# Convenience functions for quick access

def get_latest_news(symbol, limit=5):
    """
    Get the most recent news for a symbol.

    Args:
        symbol: Stock ticker symbol
        limit: Number of articles to return (default 5)

    Returns:
        List of news articles, most recent first
    """
    client = FinnhubClient()
    articles = client.get_company_news(symbol, days_back=7)
    return articles[:limit]


def get_top_news_article(symbol):
    """
    Get the single most recent/relevant news article for a symbol.

    Returns:
        Dict with headline, summary, source, url or None if no news found
    """
    articles = get_latest_news(symbol, limit=1)
    return articles[0] if articles else None


def format_news_for_display(article):
    """
    Format a news article for display in the UI.

    Args:
        article: Article dict from Finnhub

    Returns:
        Formatted string summary
    """
    time_ago = datetime.now() - article['datetime']

    if time_ago.days > 0:
        time_str = f"{time_ago.days} day{'s' if time_ago.days > 1 else ''} ago"
    elif time_ago.seconds >= 3600:
        hours = time_ago.seconds // 3600
        time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        minutes = time_ago.seconds // 60
        time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"

    return {
        'headline': article['headline'],
        'summary': article['summary'],
        'source': article['source'],
        'url': article['url'],
        'time_ago': time_str,
        'datetime': article['datetime']
    }
