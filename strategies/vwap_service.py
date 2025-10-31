"""
VWAP (Volume Weighted Average Price) Service

Wave 2 Feature 2.2: Calculate intraday VWAP for tracked movers to help
determine if the current price is trading above or below the volume-weighted average.

VWAP Formula: Σ(Typical Price × Volume) / Σ(Volume)
Where Typical Price = (High + Low + Close) / 3

Trading Signals:
- Price > VWAP: Bullish (buyers willing to pay above average)
- Price < VWAP: Bearish (stock trading below average)
- Distance from VWAP indicates strength of movement
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf

from .rate_limiter import yfinance_limiter
from .cache_utils import cached
from .api_monitoring import yfinance_monitor


@dataclass
class VWAPData:
    """VWAP analysis result for a stock."""
    symbol: str
    current_price: float
    vwap: float
    distance_from_vwap: float  # Percentage difference
    distance_dollars: float     # Dollar difference
    signal: str                 # "above" or "below"
    signal_strength: str        # "strong", "moderate", "weak"
    last_updated: datetime

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'current_price': round(self.current_price, 2),
            'vwap': round(self.vwap, 2),
            'distance_from_vwap': round(self.distance_from_vwap, 2),
            'distance_dollars': round(self.distance_dollars, 2),
            'signal': self.signal,
            'signal_strength': self.signal_strength,
            'last_updated': self.last_updated.isoformat(),
        }


@yfinance_limiter
@cached(ttl_seconds=120, key_prefix='vwap')  # Cache for 2 minutes
def calculate_vwap(symbol: str) -> Optional[VWAPData]:
    """
    Calculate VWAP for a stock using intraday data.

    Args:
        symbol: Stock ticker symbol

    Returns:
        VWAPData object or None if calculation fails

    Wave 2 Feature 2.2
    """
    try:
        ticker = yf.Ticker(symbol)

        # Get today's intraday data at 5-minute intervals
        # Using 1d period to get today's data
        hist = ticker.history(period='1d', interval='5m')

        if hist.empty:
            print(f"No intraday data available for {symbol}")
            return None

        # Calculate typical price for each interval
        # Typical Price = (High + Low + Close) / 3
        hist['Typical_Price'] = (hist['High'] + hist['Low'] + hist['Close']) / 3

        # Calculate VWAP
        # VWAP = Σ(Typical Price × Volume) / Σ(Volume)
        hist['TP_Volume'] = hist['Typical_Price'] * hist['Volume']
        cumulative_tp_volume = hist['TP_Volume'].sum()
        cumulative_volume = hist['Volume'].sum()

        if cumulative_volume == 0:
            print(f"Zero volume for {symbol}")
            return None

        vwap = cumulative_tp_volume / cumulative_volume

        # Get current price (most recent close)
        current_price = hist['Close'].iloc[-1]

        # Calculate distance from VWAP
        distance_dollars = current_price - vwap
        distance_percent = (distance_dollars / vwap) * 100

        # Determine signal
        signal = "above" if current_price >= vwap else "below"

        # Determine signal strength based on distance
        abs_distance = abs(distance_percent)
        if abs_distance >= 2.0:
            signal_strength = "strong"
        elif abs_distance >= 0.5:
            signal_strength = "moderate"
        else:
            signal_strength = "weak"

        return VWAPData(
            symbol=symbol,
            current_price=float(current_price),
            vwap=float(vwap),
            distance_from_vwap=float(distance_percent),
            distance_dollars=float(distance_dollars),
            signal=signal,
            signal_strength=signal_strength,
            last_updated=datetime.now()
        )

    except Exception as e:
        print(f"Error calculating VWAP for {symbol}: {e}")
        return None


def get_vwap_signal_color(signal: str, signal_strength: str) -> str:
    """
    Get Tailwind CSS color class for VWAP signal badge.

    Args:
        signal: "above" or "below"
        signal_strength: "strong", "moderate", "weak"

    Returns:
        Tailwind CSS color classes

    Wave 2 Feature 2.2
    """
    if signal == "above":
        if signal_strength == "strong":
            return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-500"
        elif signal_strength == "moderate":
            return "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300 border-green-400"
        else:
            return "bg-green-50 text-green-600 dark:bg-green-900/10 dark:text-green-200 border-green-300"
    else:  # below
        if signal_strength == "strong":
            return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-500"
        elif signal_strength == "moderate":
            return "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300 border-red-400"
        else:
            return "bg-red-50 text-red-600 dark:bg-red-900/10 dark:text-red-200 border-red-300"


def format_vwap_signal(signal: str, distance_percent: float) -> str:
    """
    Format VWAP signal for display.

    Args:
        signal: "above" or "below"
        distance_percent: Percentage distance from VWAP

    Returns:
        Formatted string like "Above VWAP +2.3%" or "Below VWAP -1.5%"

    Wave 2 Feature 2.2
    """
    direction = signal.capitalize()
    sign = "+" if distance_percent >= 0 else ""
    return f"{direction} VWAP {sign}{distance_percent:.2f}%"
