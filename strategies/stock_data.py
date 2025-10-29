"""
Stock market data utilities using yfinance

Provides functions for fetching real-time and pre-market stock data.
"""
import yfinance as yf
import logging
from typing import Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


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
        }


def get_stock_data(symbols: List[str]) -> List[StockData]:
    """
    Fetch stock data for multiple symbols

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
            ticker = yf.Ticker(symbol)
            info = ticker.info

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
