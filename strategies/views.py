from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import PreMarketMover
from ai_service.client_factory import get_claude_client
from ai_service.models import TokenUsageLog
from ai_service.utils import calculate_cost
from .stock_data import get_stock_data, get_top_movers, format_price, format_percent, format_volume
from .finnhub_service import get_top_news_article
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def pre_market_movers(request):
    """Display pre-market movers with filtering"""
    status_filter = request.GET.get('status', 'all')

    if status_filter == 'all':
        movers = PreMarketMover.objects.all()
    else:
        movers = PreMarketMover.objects.filter(status=status_filter)

    # Get scan results from session (keep them persistent)
    scan_results = request.session.get('scan_results', None)
    scan_filters = request.session.get('scan_filters', {})
    scan_timestamp = request.session.get('scan_timestamp', None)
    validation_warnings = request.session.pop('validation_warnings', None)
    scan_error = request.session.pop('scan_error', None)

    # Get API toggle state (default: disabled for safety)
    api_enabled = request.session.get('api_enabled', False)
    logger.info(f"Pre-market movers view loaded: api_enabled={api_enabled}, session_key={request.session.session_key}")

    # Pagination for scan results
    paginated_results = None
    page_info = None
    if scan_results:
        from django.core.paginator import Paginator
        page_number = request.GET.get('page', 1)
        paginator = Paginator(scan_results, 50)  # 50 results per page
        page_obj = paginator.get_page(page_number)
        paginated_results = page_obj.object_list
        page_info = {
            'current': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_results': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
        }

    return render(request, 'strategies/pre_market_movers.html', {
        'movers': movers,
        'status_filter': status_filter,
        'scan_results': paginated_results,
        'page_info': page_info,
        'scan_filters': scan_filters,
        'scan_timestamp': scan_timestamp,
        'api_enabled': api_enabled,
        'validation_warnings': validation_warnings,
        'scan_error': scan_error,
    })


@login_required
def add_mover(request):
    """Add a new pre-market mover"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    symbol = request.POST.get('symbol', '').strip().upper()
    company_name = request.POST.get('company_name', '').strip()
    news_headline = request.POST.get('news_headline', '').strip()
    news_source = request.POST.get('news_source', '').strip()
    news_url = request.POST.get('news_url', '').strip()
    movement_percent = request.POST.get('movement_percent', '')
    action = request.POST.get('action', 'add')

    if not symbol or not news_headline:
        return redirect('strategies:pre_market_movers')

    # Create mover
    mover = PreMarketMover.objects.create(
        symbol=symbol,
        company_name=company_name,
        news_headline=news_headline,
        news_source=news_source,
        news_url=news_url,
        movement_percent=movement_percent if movement_percent else None,
        status='identified'
    )

    # If user requested AI analysis
    if action == 'analyze':
        analyze_mover(mover)

    return redirect('strategies:pre_market_movers')


def analyze_mover(mover):
    """Get AI analysis of a pre-market mover opportunity with news research"""

    # First, try to auto-fetch news if we don't have a real headline
    if not mover.news_headline or 'Pre-market movement' in mover.news_headline or 'price movement' in mover.news_headline.lower():
        logger.info(f"Auto-fetching news for {mover.symbol}")
        try:
            top_article = get_top_news_article(mover.symbol)
            if top_article:
                mover.news_headline = top_article['headline']
                mover.news_source = top_article['source']
                mover.news_url = top_article['url']
                mover.save()
                logger.info(f"Updated {mover.symbol} with Finnhub news: {top_article['headline'][:50]}...")
        except Exception as e:
            logger.warning(f"Could not fetch news for {mover.symbol}: {e}")

    client = get_claude_client()

    # Build context with news summary if available
    news_context = f"{mover.news_headline}"
    if mover.news_source:
        news_context += f" (Source: {mover.news_source})"

    prompt = f"""Analyze this stock trading opportunity based on recent news:

Symbol: {mover.symbol}
Company: {mover.company_name or 'Unknown'}
News: {news_context}
Price Movement: {mover.movement_percent}% change

Tasks:
1. Explain what the news means for the stock price
2. Assess if this is a trading opportunity (bullish) or risk (bearish)
3. Identify key factors to watch and suggest entry strategy

Provide a concise analysis (2-3 sentences) and sentiment.

Respond in JSON format:
{{
    "analysis": "Brief analysis covering the news catalyst and trading implications...",
    "sentiment": "bullish/bearish/neutral"
}}
"""

    response = client.analyze_stock_opportunity(prompt)

    if response.success:
        try:
            # Log token usage
            TokenUsageLog.objects.create(
                endpoint='analyze',
                model=response.token_usage.model,
                prompt_tokens=response.token_usage.prompt_tokens,
                completion_tokens=response.token_usage.completion_tokens,
                total_tokens=response.token_usage.total_tokens,
                cost_estimate=calculate_cost(response.token_usage)
            )

            # Try to parse JSON response
            data = json.loads(response.content)
            mover.ai_analysis = data.get('analysis', response.content)
            mover.sentiment = data.get('sentiment', '')
            mover.status = 'researching'
            mover.save()

        except json.JSONDecodeError:
            # If not valid JSON, just save the content as analysis
            mover.ai_analysis = response.content[:500]  # Limit length
            mover.status = 'researching'
            mover.save()
            logger.warning(f"Could not parse AI response as JSON for mover {mover.id}")

    else:
        logger.error(f"Failed to get AI analysis for mover {mover.id}: {response.error_message}")


@login_required
def scan_movers(request):
    """Scan for pre-market movers using real market data with filters"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    discovery_mode = request.POST.get('discovery_mode', '').lower() == 'true'
    validation_errors = []

    # Get and validate filter parameters
    universe_name = request.POST.get('universe', 'comprehensive')

    # Validate universe name
    if discovery_mode:
        from strategies.market_universe import get_market_universe
        valid_universes = [
            'comprehensive', 'all', 'sp500', 'sp500_extended', 'nasdaq',
            'retail', 'etfs', 'ipos', 'short',
            'biotech', 'semiconductor', 'ev', 'crypto', 'defense',
            'cloud', 'fintech', 'gaming', 'ecommerce', 'energy',
            'chinese', 'smallcap'
        ]
        if universe_name not in valid_universes:
            logger.warning(f"Invalid universe name: {universe_name}, using default 'comprehensive'")
            universe_name = 'comprehensive'
            validation_errors.append(f"Invalid universe '{universe_name}', using 'comprehensive'")

    # Validate threshold (default: 2.5%)
    try:
        threshold = float(request.POST.get('threshold', '2.5'))
        if threshold < 0 or threshold > 100:
            validation_errors.append(f"Threshold must be between 0-100%, using default 2.5%")
            threshold = 2.5
    except (ValueError, TypeError):
        threshold = 2.5
        validation_errors.append("Invalid threshold value, using default 2.5%")
        logger.warning(f"Invalid threshold value: {request.POST.get('threshold')}, using default 2.5")

    # Validate min_rvol (default: 0 = any)
    try:
        min_rvol = float(request.POST.get('min_rvol', '0'))
        if min_rvol < 0:
            validation_errors.append("RVOL cannot be negative, using 0")
            min_rvol = 0
    except (ValueError, TypeError):
        min_rvol = 0
        validation_errors.append("Invalid RVOL value, using default 0")
        logger.warning(f"Invalid min_rvol value: {request.POST.get('min_rvol')}, using default 0")

    # Validate max_spread (default: 999 = any)
    try:
        max_spread = float(request.POST.get('max_spread', '999'))
        if max_spread < 0:
            validation_errors.append("Spread cannot be negative, using 999 (any)")
            max_spread = 999
    except (ValueError, TypeError):
        max_spread = 999
        validation_errors.append("Invalid spread value, using default 999")
        logger.warning(f"Invalid max_spread value: {request.POST.get('max_spread')}, using default 999")

    # Discovery mode: scan market universe
    if discovery_mode:
        from strategies.market_universe import get_market_universe
        symbols = get_market_universe(universe_name)
        logger.info(f"Discovery scan started: {len(symbols)} symbols from '{universe_name}', threshold {threshold}%")
    else:
        # Manual mode: parse user-provided symbols
        symbols_to_scan = request.POST.get('symbols_to_scan', '').strip()
        if not symbols_to_scan:
            return redirect('strategies:pre_market_movers')

        # Parse and validate symbols
        symbols = []
        for s in symbols_to_scan.split(','):
            symbol = s.strip().upper()
            if symbol:
                # Validate symbol format (letters only, 1-5 chars)
                if symbol.isalpha() and 1 <= len(symbol) <= 5:
                    symbols.append(symbol)
                else:
                    validation_errors.append(f"Invalid symbol format: {symbol} (must be 1-5 letters)")

        # Limit to 50 symbols in manual mode
        if len(symbols) > 50:
            validation_errors.append(f"Too many symbols ({len(symbols)}), limited to first 50")
            symbols = symbols[:50]

        if not symbols:
            validation_errors.append("No valid symbols provided")
            return redirect('strategies:pre_market_movers')

    # Fetch stock data
    try:
        stocks = get_top_movers(symbols, limit=100 if discovery_mode else 20)

        # Apply filters
        filtered_stocks = []
        for stock in stocks:
            # Threshold filter
            if abs(stock.change_percent) < threshold:
                continue

            # RVOL filter
            if min_rvol > 0 and (stock.relative_volume_ratio is None or stock.relative_volume_ratio < min_rvol):
                continue

            # Spread filter
            if max_spread < 999 and (stock.spread_percent is None or stock.spread_percent > max_spread):
                continue

            filtered_stocks.append(stock)

        logger.info(f"Discovery scan: {len(filtered_stocks)} movers found after filters (threshold: {threshold}%, RVOL: {min_rvol}x, spread: {max_spread}%)")

        # Convert to dict format for template
        results = []
        for stock in filtered_stocks:
            results.append({
                'symbol': stock.symbol,
                'company_name': stock.company_name,
                'current_price': format_price(stock.display_price),
                'current_price_raw': stock.display_price,
                'previous_close': format_price(stock.previous_close),
                'change_percent': format_percent(stock.change_percent),
                'change_percent_raw': stock.change_percent,
                'volume': format_volume(stock.pre_market_volume or stock.regular_market_volume),
                'has_pre_market': stock.has_pre_market_data,
                # Phase 1: Volume Metrics
                'pre_market_volume': stock.pre_market_volume,
                'average_volume': stock.average_volume,
                'relative_volume_ratio': stock.relative_volume_ratio,
                'spread_percent': stock.spread_percent,
            })

        # Store results and filters in session (persistent across page loads)
        from django.utils import timezone

        # Preserve api_enabled state explicitly
        api_enabled = request.session.get('api_enabled', False)

        request.session['scan_results'] = results
        request.session['scan_filters'] = {
            'universe': universe_name,
            'threshold': threshold,
            'min_rvol': min_rvol,
            'max_spread': max_spread,
        }
        request.session['scan_timestamp'] = timezone.now().isoformat()
        request.session['api_enabled'] = api_enabled  # Explicitly preserve

        # Store validation warnings if any
        if validation_errors:
            request.session['validation_warnings'] = validation_errors
            logger.warning(f"Validation warnings during scan: {validation_errors}")
        else:
            request.session.pop('validation_warnings', None)

        request.session.modified = True  # Force session save

        logger.info(f"Scan complete: {len(results)} results, api_enabled={api_enabled}, session_key={request.session.session_key}")

    except Exception as e:
        logger.error(f"Error scanning movers: {str(e)}")
        request.session['scan_results'] = []
        request.session['scan_error'] = str(e)

    return redirect('strategies:pre_market_movers')


@login_required
def quick_add_mover(request):
    """Quick-add a mover from scan results with auto-news fetching"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    symbol = request.POST.get('symbol', '').strip().upper()
    company_name = request.POST.get('company_name', '').strip()
    current_price = request.POST.get('current_price', '')
    change_percent = request.POST.get('change_percent', '')

    if symbol:
        # Parse movement_percent from formatted string (e.g., "+5.23%" -> 5.23)
        movement_percent = None
        if change_percent:
            try:
                # Remove "+" and "%" characters and convert to float
                clean_percent = change_percent.replace('+', '').replace('%', '').strip()
                if clean_percent and clean_percent != 'N/A':
                    movement_percent = float(clean_percent)
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse movement_percent: {change_percent}")

        # Try to auto-fetch news from Finnhub
        news_headline = f"Pre-market movement: {change_percent}" if change_percent else "Significant price movement"
        news_source = ''
        news_url = ''

        try:
            logger.info(f"Fetching news for {symbol} via Finnhub...")
            top_article = get_top_news_article(symbol)
            if top_article:
                news_headline = top_article['headline']
                news_source = top_article['source']
                news_url = top_article['url']
                logger.info(f"Found news for {symbol}: {news_headline[:50]}...")
        except Exception as e:
            logger.warning(f"Could not fetch news for {symbol}: {e}, using default headline")

        # Fetch volume metrics
        pre_market_volume = None
        average_volume = None
        relative_volume_ratio = None
        spread_percent = None

        try:
            logger.info(f"Fetching volume metrics for {symbol}...")
            stock_data_list = get_stock_data([symbol])
            if stock_data_list:
                stock = stock_data_list[0]
                pre_market_volume = stock.pre_market_volume
                average_volume = stock.average_volume
                relative_volume_ratio = stock.relative_volume_ratio
                spread_percent = stock.spread_percent
        except Exception as e:
            logger.warning(f"Could not fetch volume metrics for {symbol}: {e}")

        PreMarketMover.objects.create(
            symbol=symbol,
            company_name=company_name,
            news_headline=news_headline,
            news_source=news_source,
            news_url=news_url,
            movement_percent=movement_percent,
            # Phase 1: Volume Metrics
            pre_market_volume=pre_market_volume,
            average_volume=average_volume,
            relative_volume_ratio=relative_volume_ratio,
            spread_percent=spread_percent,
            status='identified'
        )

    return redirect('strategies:pre_market_movers')


@login_required
def research_mover(request, mover_id):
    """Get AI analysis for an existing mover"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    try:
        mover = PreMarketMover.objects.get(id=mover_id)
        analyze_mover(mover)
    except PreMarketMover.DoesNotExist:
        logger.error(f"Mover with id {mover_id} not found")

    return redirect('strategies:pre_market_movers')


@login_required
def delete_mover(request, mover_id):
    """Delete a single pre-market mover"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    try:
        mover = PreMarketMover.objects.get(id=mover_id)
        symbol = mover.symbol
        mover.delete()
        logger.info(f"Deleted mover: {symbol} (ID: {mover_id})")
    except PreMarketMover.DoesNotExist:
        logger.error(f"Mover with id {mover_id} not found")

    return redirect('strategies:pre_market_movers')


@login_required
def delete_all_movers(request):
    """Delete all pre-market movers"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    count = PreMarketMover.objects.count()
    PreMarketMover.objects.all().delete()
    logger.info(f"Deleted all {count} movers")

    return redirect('strategies:pre_market_movers')


@login_required
def toggle_api(request):
    """Toggle API usage on/off (session-based)"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    current_state = request.session.get('api_enabled', False)
    new_state = not current_state
    request.session['api_enabled'] = new_state
    request.session.modified = True

    # Force session save
    request.session.save()

    logger.info(f"API usage toggled from {current_state} to {new_state}, session key: {request.session.session_key}")
    return redirect('strategies:pre_market_movers')


@login_required
def api_usage(request):
    """Display API token usage statistics"""
    from ai_service.models import TokenUsageLog
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta

    # Get all logs
    all_logs = TokenUsageLog.objects.all().order_by('-timestamp')

    # Calculate totals
    total_stats = TokenUsageLog.objects.aggregate(
        total_tokens=Sum('total_tokens'),
        total_requests=Count('id'),
        total_prompt_tokens=Sum('prompt_tokens'),
        total_completion_tokens=Sum('completion_tokens'),
    )

    # Today's stats
    today = timezone.now().date()
    today_stats = TokenUsageLog.objects.filter(
        timestamp__date=today
    ).aggregate(
        total_tokens=Sum('total_tokens'),
        total_requests=Count('id'),
    )

    # This week's stats
    week_ago = timezone.now() - timedelta(days=7)
    week_stats = TokenUsageLog.objects.filter(
        timestamp__gte=week_ago
    ).aggregate(
        total_tokens=Sum('total_tokens'),
        total_requests=Count('id'),
    )

    # Cost estimates (using Sonnet pricing)
    # $3 per 1M input tokens, $15 per 1M output tokens
    total_cost = 0
    if total_stats['total_prompt_tokens']:
        total_cost += (total_stats['total_prompt_tokens'] / 1_000_000) * 3
    if total_stats['total_completion_tokens']:
        total_cost += (total_stats['total_completion_tokens'] / 1_000_000) * 15

    today_cost = 0
    if today_stats['total_tokens']:
        # Rough estimate: assume 70% completion tokens
        today_cost = (today_stats['total_tokens'] / 1_000_000) * 12

    week_cost = 0
    if week_stats['total_tokens']:
        week_cost = (week_stats['total_tokens'] / 1_000_000) * 12

    # Recent logs (last 50)
    recent_logs = all_logs[:50]

    return render(request, 'strategies/api_usage.html', {
        'total_stats': total_stats,
        'today_stats': today_stats,
        'week_stats': week_stats,
        'total_cost': total_cost,
        'today_cost': today_cost,
        'week_cost': week_cost,
        'recent_logs': recent_logs,
    })
