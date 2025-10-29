from django.shortcuts import render, redirect
from django.utils import timezone
from .models import PreMarketMover
from ai_service.client_factory import get_claude_client
from ai_service.models import TokenUsageLog
from ai_service.utils import calculate_cost
from .stock_data import get_stock_data, get_top_movers, format_price, format_percent, format_volume
import json
import logging

logger = logging.getLogger(__name__)


def pre_market_movers(request):
    """Display pre-market movers with filtering"""
    status_filter = request.GET.get('status', 'all')

    if status_filter == 'all':
        movers = PreMarketMover.objects.all()
    else:
        movers = PreMarketMover.objects.filter(status=status_filter)

    # Get scan results from session if they exist
    scan_results = request.session.pop('scan_results', None)
    symbols_to_scan = request.session.pop('symbols_to_scan', '')

    return render(request, 'strategies/pre_market_movers.html', {
        'movers': movers,
        'status_filter': status_filter,
        'scan_results': scan_results,
        'symbols_to_scan': symbols_to_scan
    })


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
    client = get_claude_client()

    prompt = f"""Research recent news (past 24-48 hours) for this stock and provide analysis:

Symbol: {mover.symbol}
Company: {mover.company_name or 'Unknown'}
Current Info: {mover.news_headline}
Price Movement: {mover.movement_percent}% (if available)

Tasks:
1. Find and summarize the most significant recent news about this stock
2. Explain what the news means for the stock price
3. Assess if this is a trading opportunity (bullish) or risk (bearish)
4. Identify key factors to watch

Provide a concise analysis (2-3 sentences) and sentiment.

Respond in JSON format:
{{
    "analysis": "Brief analysis covering the news catalyst and trading implications...",
    "sentiment": "bullish/bearish/neutral"
}}
"""

    response = client.validate_question(prompt)  # Reusing validate_question for simple analysis

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


def scan_movers(request):
    """Scan for pre-market movers using real market data"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    symbols_to_scan = request.POST.get('symbols_to_scan', '').strip()

    if not symbols_to_scan:
        return redirect('strategies:pre_market_movers')

    # Parse symbols
    symbols = [s.strip().upper() for s in symbols_to_scan.split(',') if s.strip()]

    # Fetch stock data
    try:
        stocks = get_top_movers(symbols, limit=20)

        # Convert to dict format for template
        results = []
        for stock in stocks:
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
            })

        # Store results and symbols in session
        request.session['scan_results'] = results
        request.session['symbols_to_scan'] = symbols_to_scan

    except Exception as e:
        logger.error(f"Error scanning movers: {str(e)}")
        request.session['scan_results'] = []
        request.session['scan_error'] = str(e)

    return redirect('strategies:pre_market_movers')


def quick_add_mover(request):
    """Quick-add a mover from scan results"""
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

        # Create a basic news headline from the price movement
        news_headline = f"Pre-market movement: {change_percent}" if change_percent else "Significant price movement"

        PreMarketMover.objects.create(
            symbol=symbol,
            company_name=company_name,
            news_headline=news_headline,
            movement_percent=movement_percent,
            status='identified'
        )

    return redirect('strategies:pre_market_movers')


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
