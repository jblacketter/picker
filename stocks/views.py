from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WatchlistItem


@login_required
def watchlist(request):
    """Display stock watchlist"""
    status_filter = request.GET.get('status', 'all')

    if status_filter == 'all':
        stocks = WatchlistItem.objects.all()
    else:
        stocks = WatchlistItem.objects.filter(status=status_filter)

    return render(request, 'stocks/watchlist.html', {
        'stocks': stocks,
        'status_filter': status_filter
    })


@login_required
def add_to_watchlist(request):
    """Add a stock to the watchlist"""
    if request.method != 'POST':
        return redirect('stocks:watchlist')

    symbol = request.POST.get('symbol', '').strip().upper()
    company_name = request.POST.get('company_name', '').strip()

    if symbol:
        WatchlistItem.objects.get_or_create(
            symbol=symbol,
            defaults={'company_name': company_name}
        )

    return redirect('stocks:watchlist')
