"""
Django Management Command: Scan Pre-Market Movers

Automatically scans a watchlist for stocks with significant pre-market movement,
fetches news from Finnhub, and creates PreMarketMover records for review.

Usage:
    python manage.py scan_premarket_movers
    python manage.py scan_premarket_movers --watchlist aggressive
    python manage.py scan_premarket_movers --threshold 3.0
    python manage.py scan_premarket_movers --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from strategies.models import PreMarketMover
from strategies.watchlists import get_watchlist, combine_watchlists
from strategies.market_universe import get_market_universe
from strategies.stock_data import get_top_movers
from strategies.finnhub_service import get_top_news_article
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scan watchlist for pre-market movers and auto-fetch news'

    def add_arguments(self, parser):
        parser.add_argument(
            '--discovery',
            action='store_true',
            help='Discovery mode: Scan comprehensive universe (410 stocks) with lower threshold (2.5%)'
        )
        parser.add_argument(
            '--universe',
            type=str,
            default=None,
            help='Market universe to scan (comprehensive, sp500, nasdaq, retail, biotech, all, etc.)'
        )
        parser.add_argument(
            '--watchlist',
            type=str,
            default=None,
            help='Use custom watchlist instead (default, aggressive, conservative, meme, earnings)'
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=None,
            help='Minimum absolute % change to qualify as a mover (default: 5.0, or 2.5 in discovery mode)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of movers to track (default: 20)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records'
        )
        parser.add_argument(
            '--skip-news',
            action='store_true',
            help='Skip news fetching (faster, for testing)'
        )

    def handle(self, *args, **options):
        discovery_mode = options['discovery']
        universe_name = options['universe']
        watchlist_name = options['watchlist']
        threshold = options['threshold']
        limit = options['limit']
        dry_run = options['dry_run']
        skip_news = options['skip_news']

        # Discovery mode defaults
        if discovery_mode:
            if universe_name is None:
                universe_name = 'comprehensive'
            if threshold is None:
                threshold = 2.5
        else:
            if universe_name is None:
                universe_name = 'comprehensive'
            if threshold is None:
                threshold = 5.0

        mode_label = 'DISCOVERY MODE' if discovery_mode else 'PRE-MARKET MOVERS SCANNER'
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'{mode_label}\n'
            f'{"="*60}\n'
        ))

        if discovery_mode:
            self.stdout.write(self.style.SUCCESS(
                '🔍 Scanning comprehensive market universe for movers...\n'
            ))

        # Load symbols - use watchlist if specified, otherwise use market universe
        if watchlist_name:
            symbols = get_watchlist(watchlist_name)
            source = f'Watchlist: {watchlist_name}'
        else:
            symbols = get_market_universe(universe_name)
            source = f'Market Universe: {universe_name}'

        self.stdout.write(source)
        self.stdout.write(f'Symbols: {len(symbols)} ({", ".join(symbols[:10])}...)')
        self.stdout.write(f'Threshold: ±{threshold}%')
        self.stdout.write(f'Limit: {limit} movers\n')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No records will be created\n'))

        # Scan for movers
        self.stdout.write('Fetching market data...')
        try:
            movers = get_top_movers(symbols, limit=limit)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching market data: {e}'))
            logger.error(f'Market data fetch failed: {e}')
            return

        if not movers:
            self.stdout.write(self.style.WARNING('No market data returned'))
            return

        # Filter by threshold
        filtered_movers = [
            m for m in movers
            if abs(m.change_percent) >= threshold
        ]

        self.stdout.write(
            f'Found {len(movers)} stocks, {len(filtered_movers)} meet threshold\n'
        )

        if not filtered_movers:
            self.stdout.write(self.style.WARNING(
                f'No stocks moving ±{threshold}% or more. Try lowering threshold.'
            ))
            return

        # Process each mover
        created_count = 0
        skipped_count = 0

        for mover in filtered_movers:
            symbol = mover.symbol
            company_name = mover.company_name
            movement = mover.change_percent
            price = mover.display_price

            self.stdout.write(f'\n📊 {symbol} ({company_name})')
            self.stdout.write(f'   Price: ${price:.2f}  Change: {movement:+.2f}%')

            # Display volume metrics
            rvol = mover.relative_volume_ratio
            spread = mover.spread_percent
            if rvol:
                rvol_indicator = '🔥' if rvol >= 3.0 else '⚡' if rvol >= 2.0 else ''
                self.stdout.write(f'   RVOL: {rvol:.2f}x {rvol_indicator}')
            if spread:
                spread_indicator = '⚠️' if spread > 2.0 else ''
                self.stdout.write(f'   Spread: {spread:.3f}% {spread_indicator}')

            # Check if already tracked today
            today = timezone.now().date()
            existing = PreMarketMover.objects.filter(
                symbol=symbol,
                identified_date__date=today
            ).first()

            if existing:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠️  Already tracked today (ID: {existing.id}) - SKIPPED'
                ))
                skipped_count += 1
                continue

            # Fetch news
            news_headline = f'Pre-market movement: {movement:+.2f}%'
            news_source = ''
            news_url = ''

            if not skip_news:
                self.stdout.write('   Fetching news from Finnhub...')
                try:
                    article = get_top_news_article(symbol)
                    if article:
                        news_headline = article['headline']
                        news_source = article['source']
                        news_url = article['url']
                        self.stdout.write(f'   📰 {news_headline[:60]}...')
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠️  No news found'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  News fetch failed: {e}'))
                    logger.warning(f'News fetch failed for {symbol}: {e}')

            # Create record
            if not dry_run:
                try:
                    new_mover = PreMarketMover.objects.create(
                        symbol=symbol,
                        company_name=company_name,
                        news_headline=news_headline,
                        news_source=news_source,
                        news_url=news_url,
                        movement_percent=movement,
                        pre_market_price=price,
                        # Phase 1: Volume Metrics
                        pre_market_volume=mover.pre_market_volume,
                        average_volume=mover.average_volume,
                        relative_volume_ratio=mover.relative_volume_ratio,
                        spread_percent=mover.spread_percent,
                        status='identified'
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'   ✅ Tracked (ID: {new_mover.id})'
                    ))
                    created_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Failed to create: {e}'))
                    logger.error(f'Failed to create mover for {symbol}: {e}')
            else:
                self.stdout.write(self.style.SUCCESS('   ✅ Would create (DRY RUN)'))
                created_count += 1

        # Summary
        self.stdout.write(
            f'\n{"="*60}\n'
            f'SUMMARY\n'
            f'{"="*60}\n'
        )
        self.stdout.write(f'Scanned: {len(symbols)} symbols')
        self.stdout.write(f'Moving ±{threshold}%: {len(filtered_movers)} stocks')
        self.stdout.write(f'Created: {created_count} new movers')
        self.stdout.write(f'Skipped: {skipped_count} (already tracked today)')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No actual changes made'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Done! Check dashboard at /strategies/pre-market-movers/'
            ))

        self.stdout.write('')  # Blank line
