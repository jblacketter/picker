"""
Discovery APIs - External APIs for market mover discovery

Provides interfaces to APIs that can discover pre-market movers without
requiring a predefined symbol list.
"""
import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class FMPClient:
    """
    Financial Modeling Prep API client for market discovery

    Free tier endpoints for discovering market movers:
    - /gainers - Top gainers (updated every 15 minutes)
    - /losers - Top losers (updated every 15 minutes)
    - /actives - Most active by volume (updated every 15 minutes)

    Note: /stock_market/* endpoints require paid plan
    """

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP client

        Args:
            api_key: FMP API key (defaults to settings.FMP_API_KEY)
        """
        self.api_key = api_key or settings.FMP_API_KEY
        if not self.api_key:
            logger.warning("FMP_API_KEY not configured - API calls will fail")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Make API request to FMP

        Args:
            endpoint: API endpoint (e.g., '/stock_market/gainers')
            params: Additional query parameters

        Returns:
            List of dict responses, or None if request fails
        """
        if not self.api_key:
            logger.error("Cannot make FMP request: API key not configured")
            return None

        url = f"{self.BASE_URL}{endpoint}"
        request_params = {'apikey': self.api_key}
        if params:
            request_params.update(params)

        try:
            logger.info(f"Fetching FMP data from {endpoint}")
            response = requests.get(url, params=request_params, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"FMP returned {len(data) if isinstance(data, list) else 'non-list'} results")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"FMP API request failed for {endpoint}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse FMP JSON response: {e}")
            return None

    def get_gainers(self, limit: int = 20) -> List[Dict]:
        """
        Get top gainers from FMP (FREE TIER)

        Args:
            limit: Maximum number of results (default 20)

        Returns:
            List of dicts with keys: symbol, name, price, changesPercentage, change
        """
        data = self._make_request('/gainers')
        if data is None:
            return []

        # FMP returns all gainers, limit to requested count
        return data[:limit] if isinstance(data, list) else []

    def get_losers(self, limit: int = 20) -> List[Dict]:
        """
        Get top losers from FMP (FREE TIER)

        Args:
            limit: Maximum number of results (default 20)

        Returns:
            List of dicts with keys: symbol, name, price, changesPercentage, change
        """
        data = self._make_request('/losers')
        if data is None:
            return []

        return data[:limit] if isinstance(data, list) else []

    def get_actives(self, limit: int = 20) -> List[Dict]:
        """
        Get most active stocks by volume (FREE TIER)

        Args:
            limit: Maximum number of results (default 20)

        Returns:
            List of dicts with keys: symbol, name, price, changesPercentage, change
        """
        data = self._make_request('/actives')
        if data is None:
            return []

        return data[:limit] if isinstance(data, list) else []

    def get_gainers_and_losers(self, limit: int = 20) -> List[Dict]:
        """
        Get combined list of top gainers and losers

        Args:
            limit: Maximum number of each type (default 20, returns up to 40 total)

        Returns:
            Combined list sorted by absolute percent change
        """
        gainers = self.get_gainers(limit)
        losers = self.get_losers(limit)

        combined = gainers + losers

        # Sort by absolute percent change (biggest movers first)
        combined.sort(key=lambda x: abs(x.get('changesPercentage', 0)), reverse=True)

        return combined


def test_fmp_connection():
    """
    Test FMP API connection and data quality

    Prints detailed info about response format and data freshness.
    Used for evaluating if FMP is suitable for pre-market discovery.
    """
    print("\n" + "="*60)
    print("TESTING FMP API CONNECTION")
    print("="*60 + "\n")

    client = FMPClient()

    if not client.api_key:
        print("❌ ERROR: FMP_API_KEY not configured in .env file")
        print("\nTo use FMP API:")
        print("1. Sign up at https://financialmodelingprep.com/")
        print("2. Add FMP_API_KEY=your_key_here to .env")
        return

    # Test gainers endpoint
    print("Testing /gainers (FREE TIER)...")
    gainers = client.get_gainers(limit=5)

    if gainers:
        print(f"✅ SUCCESS: Retrieved {len(gainers)} gainers\n")
        print("Sample data (top 3):")
        for i, stock in enumerate(gainers[:3], 1):
            print(f"\n{i}. {stock.get('symbol', 'N/A')} - {stock.get('name', 'N/A')}")
            print(f"   Price: ${stock.get('price', 0):.2f}")
            print(f"   Change: {stock.get('changesPercentage', 0):+.2f}%")
            print(f"   Change $: ${stock.get('change', 0):+.2f}")
    else:
        print("❌ FAILED: No data returned from gainers endpoint")

    # Test losers endpoint
    print("\n" + "-"*60)
    print("Testing /losers (FREE TIER)...")
    losers = client.get_losers(limit=5)

    if losers:
        print(f"✅ SUCCESS: Retrieved {len(losers)} losers\n")
        print("Sample data (top 3):")
        for i, stock in enumerate(losers[:3], 1):
            print(f"\n{i}. {stock.get('symbol', 'N/A')} - {stock.get('name', 'N/A')}")
            print(f"   Price: ${stock.get('price', 0):.2f}")
            print(f"   Change: {stock.get('changesPercentage', 0):+.2f}%")
            print(f"   Change $: ${stock.get('change', 0):+.2f}")
    else:
        print("❌ FAILED: No data returned from losers endpoint")

    # Summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    if gainers or losers:
        print("✅ FMP API is working")
        print("\nNext steps:")
        print("1. Test during pre-market hours (4:00-9:30 AM ET)")
        print("2. Check if data reflects pre-market moves or previous day's close")
        print("3. Monitor update frequency")
        print("4. Evaluate data quality vs. yfinance scanner")
    else:
        print("❌ FMP API test failed")
        print("\nCheck:")
        print("- API key is correct in .env")
        print("- Free tier limits not exceeded")
        print("- Network connectivity")

    print("")


if __name__ == "__main__":
    # Run test when module executed directly
    test_fmp_connection()
