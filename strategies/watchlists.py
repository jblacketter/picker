"""
Watchlist Configuration for Automated Scanning

Define symbol lists for different scanning strategies.
These are used by the automated morning scanner to identify pre-market movers.
"""

# Default watchlist for pre-market scanning
# Focus on high-volume, news-driven stocks
DEFAULT_WATCHLIST = [
    # Mega Cap Tech
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Alphabet
    'AMZN',   # Amazon
    'META',   # Meta
    'TSLA',   # Tesla

    # Semiconductor / AI
    'NVDA',   # Nvidia
    'AMD',    # AMD
    'INTC',   # Intel
    'AVGO',   # Broadcom

    # High-Beta Tech
    'NFLX',   # Netflix
    'SHOP',   # Shopify
    'SQ',     # Block (Square)
    'COIN',   # Coinbase
    'ROKU',   # Roku

    # Finance
    'JPM',    # JPMorgan
    'BAC',    # Bank of America
    'GS',     # Goldman Sachs

    # Healthcare / Biotech
    'JNJ',    # Johnson & Johnson
    'PFE',    # Pfizer
    'MRNA',   # Moderna

    # Energy
    'XOM',    # Exxon
    'CVX',    # Chevron

    # Other High-Volume
    'DIS',    # Disney
    'BABA',   # Alibaba
    'NIO',    # NIO
]

# Aggressive watchlist - higher volatility stocks
AGGRESSIVE_WATCHLIST = [
    'TSLA', 'NVDA', 'AMD', 'COIN', 'SHOP', 'SQ',
    'ROKU', 'NFLX', 'MRNA', 'NIO', 'BABA',
    'PLTR', 'ARKK', 'SPCE', 'LCID', 'RIVN'
]

# Conservative watchlist - blue chips only
CONSERVATIVE_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM',
    'JNJ', 'PFE', 'XOM', 'CVX', 'DIS', 'BAC'
]

# Popular meme stocks (use with caution)
MEME_WATCHLIST = [
    'GME', 'AMC', 'BB', 'BBBY', 'TSLA',
    'PLTR', 'WISH', 'CLOV', 'SPCE'
]

# Earnings season watchlist - update quarterly
# Add stocks with upcoming earnings here
EARNINGS_WATCHLIST = []


def get_watchlist(name='default'):
    """
    Get a watchlist by name.

    Args:
        name: Watchlist name (default, aggressive, conservative, meme, earnings)

    Returns:
        List of stock symbols
    """
    watchlists = {
        'default': DEFAULT_WATCHLIST,
        'aggressive': AGGRESSIVE_WATCHLIST,
        'conservative': CONSERVATIVE_WATCHLIST,
        'meme': MEME_WATCHLIST,
        'earnings': EARNINGS_WATCHLIST,
    }

    return watchlists.get(name.lower(), DEFAULT_WATCHLIST)


def combine_watchlists(*names):
    """
    Combine multiple watchlists into one unique list.

    Args:
        *names: Watchlist names to combine

    Returns:
        Combined list of unique symbols
    """
    combined = []
    for name in names:
        combined.extend(get_watchlist(name))

    # Return unique symbols, preserving order
    seen = set()
    unique = []
    for symbol in combined:
        if symbol not in seen:
            seen.add(symbol)
            unique.append(symbol)

    return unique
