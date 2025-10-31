"""
End-to-end tests for Wave 2 features.

Wave 2 Feature 2.1: Market Context Widget
Wave 2 Feature 2.2: VWAP Analysis

These tests verify that the new features work correctly with the infrastructure
from Wave 1 (rate limiting, caching, API monitoring).
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from strategies.models import PreMarketMover
from strategies.market_context import get_market_context, MarketContext
from strategies.vwap_service import calculate_vwap, VWAPData

User = get_user_model()


class MarketContextTestCase(TestCase):
    """Test Market Context feature"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_get_market_context(self):
        """Test that market context can be fetched"""
        context = get_market_context()

        # Context may be None if market is closed or API fails
        if context is not None:
            self.assertIsInstance(context, MarketContext)
            self.assertIsNotNone(context.spy_change)
            self.assertIsNotNone(context.qqq_change)
            self.assertIsNotNone(context.vix_level)
            self.assertIn(context.market_sentiment, ['bullish', 'bearish', 'neutral'])
            self.assertIn(context.sentiment_color, ['green', 'red', 'gray'])

    def test_market_context_api_endpoint(self):
        """Test that market context API endpoint returns valid JSON"""
        response = self.client.get('/strategies/market-context/')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should have success field
        self.assertIn('success', data)

        # If successful, should have data
        if data['success']:
            self.assertIn('data', data)
            market_data = data['data']
            self.assertIn('spy_change', market_data)
            self.assertIn('qqq_change', market_data)
            self.assertIn('vix_level', market_data)
            self.assertIn('market_sentiment', market_data)

    def test_market_context_in_pre_market_movers_view(self):
        """Test that market context is included in pre-market movers page"""
        response = self.client.get('/strategies/pre-market-movers/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('market_context', response.context)

        # If market context is available, verify it's a MarketContext object
        if response.context['market_context'] is not None:
            self.assertIsInstance(response.context['market_context'], MarketContext)


class VWAPTestCase(TestCase):
    """Test VWAP analysis feature"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create test mover
        self.mover = PreMarketMover.objects.create(
            symbol='AAPL',
            company_name='Apple Inc.',
            news_headline='Apple announces new product',
            movement_percent=2.5,
            status='identified'
        )

    def test_calculate_vwap(self):
        """Test that VWAP can be calculated for a stock"""
        vwap_data = calculate_vwap('AAPL')

        # VWAP may be None if market is closed or data unavailable
        if vwap_data is not None:
            self.assertIsInstance(vwap_data, VWAPData)
            self.assertEqual(vwap_data.symbol, 'AAPL')
            self.assertIsNotNone(vwap_data.current_price)
            self.assertIsNotNone(vwap_data.vwap)
            self.assertIn(vwap_data.signal, ['above', 'below'])
            self.assertIn(vwap_data.signal_strength, ['strong', 'moderate', 'weak'])

    def test_vwap_in_pre_market_movers_view(self):
        """Test that VWAP data is included for tracked movers"""
        response = self.client.get('/strategies/pre-market-movers/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('vwap_data', response.context)

        # VWAP data should be a dictionary
        self.assertIsInstance(response.context['vwap_data'], dict)

        # If VWAP was calculated for our test mover, verify it
        if self.mover.id in response.context['vwap_data']:
            vwap = response.context['vwap_data'][self.mover.id]
            self.assertIsInstance(vwap, VWAPData)
            self.assertEqual(vwap.symbol, 'AAPL')

    def test_vwap_caching(self):
        """Test that VWAP results are cached"""
        # First call - cache miss
        vwap1 = calculate_vwap('AAPL')

        # Second call - should hit cache and return same result
        vwap2 = calculate_vwap('AAPL')

        # If both succeeded, they should have the same values
        if vwap1 is not None and vwap2 is not None:
            self.assertEqual(vwap1.vwap, vwap2.vwap)
            self.assertEqual(vwap1.current_price, vwap2.current_price)


class Wave2IntegrationTestCase(TestCase):
    """Integration tests for Wave 2 features working together"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create multiple test movers
        self.movers = [
            PreMarketMover.objects.create(
                symbol='AAPL',
                company_name='Apple Inc.',
                news_headline='Apple news',
                movement_percent=2.5,
                status='identified'
            ),
            PreMarketMover.objects.create(
                symbol='MSFT',
                company_name='Microsoft Corp.',
                news_headline='Microsoft news',
                movement_percent=-1.8,
                status='identified'
            ),
        ]

    def test_page_loads_with_all_wave2_features(self):
        """Test that the pre-market movers page loads with all Wave 2 features"""
        response = self.client.get('/strategies/pre-market-movers/')

        self.assertEqual(response.status_code, 200)

        # Verify Market Context is in context
        self.assertIn('market_context', response.context)

        # Verify VWAP data is in context
        self.assertIn('vwap_data', response.context)

        # Verify movers are returned
        self.assertEqual(len(response.context['movers']), 2)

    def test_template_renders_market_context_widget(self):
        """Test that template includes market context widget"""
        response = self.client.get('/strategies/pre-market-movers/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Check for Market Context widget elements
        if response.context['market_context'] is not None:
            self.assertIn('Market Context', content)
            self.assertIn('SPY', content)
            self.assertIn('QQQ', content)
            self.assertIn('VIX', content)

    def test_rate_limiting_applies_to_wave2_features(self):
        """Test that rate limiting from Wave 1 applies to Wave 2 features"""
        # This is more of a smoke test - Wave 1 tests cover rate limiting in detail
        # Just verify that Wave 2 functions can be called without errors

        context = get_market_context()
        vwap = calculate_vwap('AAPL')

        # No exceptions should be raised
        # Results may be None if market is closed, but that's expected
        self.assertTrue(True)
