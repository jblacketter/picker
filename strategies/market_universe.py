"""
Market Universe - Comprehensive Stock Lists

Pre-built lists of stocks to scan for market-wide discovery.
These replace the need for a market screener API.
"""

# S&P 500 - Top 100 most liquid (full list is too slow for real-time scanning)
# Update periodically from: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
SP500_TOP_100 = [
    # Mega Cap Tech
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL',

    # Large Cap Tech
    'ADBE', 'CRM', 'CSCO', 'ACN', 'AMD', 'INTC', 'QCOM', 'TXN', 'INTU', 'AMAT',
    'SNOW', 'NOW', 'PANW', 'PLTR', 'UBER', 'ABNB',

    # Communication
    'NFLX', 'DIS', 'CMCSA', 'TMUS', 'VZ', 'T',

    # Finance
    'BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'SCHW', 'AXP', 'C', 'USB',
    'PNC', 'COF', 'BLK', 'SPGI',

    # Healthcare
    'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY', 'AMGN',
    'GILD', 'CVS', 'CI', 'ISRG', 'REGN', 'VRTX', 'ZTS', 'MRNA', 'BSX',

    # Consumer
    'COST', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'BKNG',

    # Industrial
    'CAT', 'BA', 'UNP', 'HON', 'UPS', 'RTX', 'DE', 'LMT', 'GE', 'MMM',

    # Energy
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO',

    # Materials
    'LIN', 'APD', 'SHW', 'FCX', 'NEM',

    # Real Estate
    'PLD', 'AMT', 'CCI', 'EQIX', 'SPG',
]

# NASDAQ 100 - Complete list (100 symbols)
NASDAQ_100 = [
    # Mega Cap
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',

    # Large Cap Tech
    'NFLX', 'ADBE', 'CSCO', 'PEP', 'TMUS', 'AMD', 'INTC', 'QCOM', 'CMCSA', 'TXN',
    'INTU', 'AMGN', 'HON', 'SBUX', 'AMAT', 'ISRG', 'BKNG', 'MDLZ', 'GILD', 'ADP',
    'VRTX', 'REGN', 'ADI', 'LRCX', 'PANW', 'MU', 'KLAC', 'SNPS', 'CDNS', 'MELI',
    'ABNB', 'MRNA', 'ASML', 'ORLY', 'CSX', 'NXPI', 'CTAS', 'FTNT', 'DASH', 'WDAY',

    # Mid-Large Cap
    'MAR', 'PYPL', 'CHTR', 'PCAR', 'CPRT', 'MRVL', 'MNST', 'CRWD', 'PAYX', 'DXCM',
    'ODFL', 'EA', 'IDXX', 'LULU', 'KDP', 'CSGP', 'BIIB', 'ON', 'DDOG', 'TTD',
    'ZS', 'FAST', 'VRSK', 'EXC', 'CTSH', 'TEAM', 'ROST', 'GEHC', 'BKR',
    'KHC', 'XEL', 'FANG', 'AEP', 'MCHP', 'CEG', 'DLTR', 'WBD', 'ENPH', 'CCEP',
    'CDW', 'ARM', 'GFS', 'ILMN', 'ZM', 'WBA', 'SMCI', 'TTWO', 'MDB', 'EBAY',
]

# High-Volume Meme/Retail Favorites
RETAIL_FAVORITES = [
    'GME', 'AMC', 'BBBY', 'BB', 'PLTR', 'SOFI', 'RIVN', 'LCID', 'NIO',
    'CLOV', 'SPCE', 'HOOD', 'COIN', 'RBLX', 'SHOP', 'SQ', 'ROKU', 'SNAP', 'PINS',
]

# Chinese ADRs - Often gap on news
CHINESE_ADRS = [
    'BABA', 'JD', 'PDD', 'BIDU', 'NIO', 'XPEV', 'LI', 'BILI', 'TME', 'IQ',
]

# Biotech - Big movers on FDA/clinical news
BIOTECH_MOVERS = [
    'MRNA', 'BNTX', 'REGN', 'VRTX', 'GILD', 'BIIB', 'SGEN', 'ALNY', 'EXEL', 'BMRN',
    'SRPT', 'TECH', 'IONS', 'NBIX', 'JAZZ', 'INCY', 'RGEN', 'UTHR',
]

# Semiconductor - AI/chip news drivers
SEMICONDUCTOR = [
    'NVDA', 'AMD', 'INTC', 'AVGO', 'QCOM', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'ASML',
    'MU', 'MRVL', 'ADI', 'NXPI', 'MCHP', 'ON', 'SWKS', 'QRVO',
]

# EV & Auto
EV_AUTO = [
    'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'F', 'GM', 'STLA',
]

# Crypto-Related
CRYPTO_EXPOSED = [
    'COIN', 'MSTR', 'RIOT', 'MARA', 'CLSK', 'HUT', 'HOOD',
]

# Defense & Aerospace
DEFENSE = [
    'LMT', 'RTX', 'BA', 'NOC', 'GD', 'LHX', 'HWM', 'TDG', 'LDOS',
]

# Recent IPOs (2023-2024) - Often volatile, high-mover potential
RECENT_IPOS = [
    'ARM', 'BIRK', 'RDDT', 'FYBR', 'KVUE', 'CART', 'IONQ', 'VRT', 'KROS', 'BNED',
    'SOUN', 'INST', 'RXRX', 'FOUR', 'BROS', 'CAVA', 'LYFT', 'DASH', 'SNOW', 'RBLX',
    'HOOD', 'COIN', 'RIVN', 'LCID', 'NU', 'SOFI', 'OPEN', 'UPST', 'AFRM', 'GTLB',
]

# High Short Interest - Squeeze potential
HIGH_SHORT_INTEREST = [
    'GME', 'AMC', 'BBBY', 'BYND', 'RIOT', 'MARA', 'CLOV', 'ROOT',
    'GOEV', 'RIDE', 'WKHS', 'TLRY', 'SNDL', 'MVIS', 'CTRM', 'OCGN', 'EXPR',
]

# Popular ETFs - High volume, news-driven
ETFS = [
    # Index
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'RSP',

    # Leveraged Bull
    'TQQQ', 'SOXL', 'UPRO', 'SPXL', 'TECL', 'FNGU', 'BULZ', 'WEBL',

    # Leveraged Bear
    'SQQQ', 'SOXS', 'SPXS', 'SDOW', 'UVXY', 'VXX',

    # Sector
    'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLU', 'XLRE',
    'SMH', 'IBB', 'XBI', 'KRE', 'XRT', 'XME', 'XOP', 'ITB', 'GDX', 'GDXJ',

    # Thematic
    'ARKK', 'ARKF', 'ARKG', 'ARKW', 'ARKQ', 'TAN', 'ICLN', 'LIT', 'JETS', 'DRIV',
]

# Additional S&P 500 Mid-Large Cap (Next 100 most liquid)
SP500_NEXT_100 = [
    # Industrial
    'EMR', 'ITW', 'NSC', 'CSX', 'FDX', 'WM', 'ETN', 'PH', 'CMI', 'CARR',

    # Consumer
    'PM', 'MO', 'EL', 'CL', 'KMB', 'GIS', 'K', 'HSY', 'SYY', 'TSN',

    # Healthcare
    'ELV', 'HUM', 'HCA', 'MCK', 'CNC', 'CAH', 'BIIB', 'ILMN', 'IDXX', 'A',
    'SYK', 'EW', 'BDX', 'RMD', 'ALGN', 'DXCM', 'ZBH', 'BAX', 'HOLX', 'PODD',

    # Finance
    'CME', 'ICE', 'MCO', 'MMC', 'AON', 'TRV', 'PGR', 'ALL', 'CB', 'AIG',
    'MET', 'PRU', 'AFL', 'AMP', 'TROW', 'BEN', 'IVZ', 'NTRS',

    # Tech/Services
    'ANET', 'NDAQ', 'KEYS', 'FTV', 'TYL', 'EPAM', 'WDC', 'STX', 'HPQ', 'NTAP',

    # Utilities
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'SRE', 'PCG', 'ED', 'EXC', 'XEL',

    # Materials
    'ECL', 'DOW', 'DD', 'PPG', 'NUE', 'VMC', 'MLM', 'ALB', 'BALL', 'PKG',

    # Real Estate
    'WELL', 'PSA', 'DLR', 'O', 'AVB', 'EQR', 'VTR', 'ESS', 'MAA', 'ARE',
]

# Russell 2000 Most Active Small Caps
RUSSELL_2000_LIQUID = [
    # High-volume small caps
    'IWM', 'MARA', 'RIOT', 'SIRI', 'PLUG', 'F', 'SOFI', 'AAL', 'UAL', 'CCL',
    'NCLH', 'RCL', 'SAVE', 'JBLU', 'DAL', 'LUV', 'ALK', 'HA', 'MESA', 'SKYW',
    'BLNK', 'CHPT', 'EVGO', 'QS', 'ARVL', 'FFIE', 'MULN', 'ELMS', 'LEV', 'FSR',
    'RIG', 'HP', 'BTU', 'ARCH', 'CEIX', 'HCC', 'METC', 'HNRG', 'WTI', 'TALO',
]

# Cloud & SaaS
CLOUD_SAAS = [
    'CRM', 'NOW', 'SNOW', 'DDOG', 'CRWD', 'ZS', 'NET', 'OKTA', 'ESTC', 'DOCU',
    'TWLO', 'MDB', 'TEAM', 'HUBS', 'ZM', 'SHOP', 'WDAY', 'VEEV', 'ZI', 'BILL',
]

# Fintech
FINTECH = [
    'SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST', 'LC', 'NU', 'OPEN',
    'ALLY', 'GS', 'MS', 'SCHW', 'IBKR', 'MKTX', 'TW', 'VIRT',
]

# Gaming & Entertainment
GAMING = [
    'EA', 'TTWO', 'ATVI', 'RBLX', 'U', 'DIS', 'NFLX', 'SPOT', 'WBD', 'PARA',
    'LYV', 'MSG', 'MSGS', 'DKNG', 'PENN', 'MGM', 'WYNN', 'LVS', 'CZR',
]

# E-commerce & Retail
ECOMMERCE = [
    'AMZN', 'SHOP', 'MELI', 'SE', 'BABA', 'JD', 'PDD', 'ETSY', 'W', 'CHWY',
    'CVNA', 'CPNG', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'UBER', 'LYFT', 'DASH',
]

# Energy & Oil
ENERGY_EXTENDED = [
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'OXY', 'DVN',
    'HAL', 'BKR', 'PXD', 'MRO', 'HES', 'APA', 'FANG', 'EQT', 'AR', 'CTRA',
]


def get_market_universe(name='comprehensive'):
    """
    Get a comprehensive list of stocks to scan for market-wide discovery.

    Args:
        name: Universe name
            - 'comprehensive': ~700 most liquid stocks (RECOMMENDED FOR DISCOVERY)
            - 'sp500': S&P 500 top 100
            - 'nasdaq': NASDAQ 100
            - 'retail': Meme stocks & retail favorites
            - 'etfs': Popular ETFs (leveraged, sector, thematic)
            - 'ipos': Recent IPOs (2023-2024)
            - 'short': High short interest stocks
            - 'all': Everything (900+ symbols, most thorough but slowest)
            - Sector-specific: biotech, semiconductor, ev, crypto, defense, cloud, fintech, gaming, ecommerce, energy

    Returns:
        List of stock symbols (deduplicated)
    """
    universes = {
        # Single categories
        'sp500': SP500_TOP_100,
        'sp500_extended': SP500_TOP_100 + SP500_NEXT_100,
        'nasdaq': NASDAQ_100,
        'retail': RETAIL_FAVORITES,
        'etfs': ETFS,
        'ipos': RECENT_IPOS,
        'short': HIGH_SHORT_INTEREST,

        # Sector-specific
        'chinese': CHINESE_ADRS,
        'biotech': BIOTECH_MOVERS,
        'semiconductor': SEMICONDUCTOR,
        'ev': EV_AUTO,
        'crypto': CRYPTO_EXPOSED,
        'defense': DEFENSE,
        'cloud': CLOUD_SAAS,
        'fintech': FINTECH,
        'gaming': GAMING,
        'ecommerce': ECOMMERCE,
        'energy': ENERGY_EXTENDED,
        'smallcap': RUSSELL_2000_LIQUID,

        # Combined universes for discovery
        'comprehensive': list(set(
            SP500_TOP_100 + SP500_NEXT_100 +  # S&P 500 top 200
            NASDAQ_100 +  # NASDAQ 100
            ETFS +  # Popular ETFs
            RETAIL_FAVORITES +  # Meme stocks
            RECENT_IPOS +  # Recent IPOs
            HIGH_SHORT_INTEREST +  # Squeeze candidates
            SEMICONDUCTOR +  # Chip stocks
            BIOTECH_MOVERS +  # Biotech
            CLOUD_SAAS +  # Cloud/SaaS
            FINTECH +  # Fintech
            CHINESE_ADRS  # Chinese ADRs
        )),

        'all': list(set(
            SP500_TOP_100 + SP500_NEXT_100 +
            NASDAQ_100 +
            ETFS +
            RETAIL_FAVORITES +
            RECENT_IPOS +
            HIGH_SHORT_INTEREST +
            CHINESE_ADRS +
            BIOTECH_MOVERS +
            SEMICONDUCTOR +
            EV_AUTO +
            CRYPTO_EXPOSED +
            DEFENSE +
            CLOUD_SAAS +
            FINTECH +
            GAMING +
            ECOMMERCE +
            ENERGY_EXTENDED +
            RUSSELL_2000_LIQUID
        )),
    }

    return universes.get(name.lower(), universes['comprehensive'])


def get_universe_info():
    """Print information about available universes."""
    print("\n" + "="*70)
    print("MARKET UNIVERSE - AVAILABLE SYMBOL LISTS")
    print("="*70)

    print("\n📊 MAIN UNIVERSES (Discovery):")
    print("-" * 70)
    for name in ['comprehensive', 'all', 'sp500', 'sp500_extended', 'nasdaq']:
        symbols = get_market_universe(name)
        print(f"  {name:18} : {len(symbols):4} symbols")

    print("\n🎯 THEMATIC LISTS:")
    print("-" * 70)
    for name in ['retail', 'etfs', 'ipos', 'short']:
        symbols = get_market_universe(name)
        print(f"  {name:18} : {len(symbols):4} symbols")

    print("\n🏭 SECTOR-SPECIFIC:")
    print("-" * 70)
    for name in ['biotech', 'semiconductor', 'ev', 'crypto', 'defense',
                 'cloud', 'fintech', 'gaming', 'ecommerce', 'energy',
                 'chinese', 'smallcap']:
        symbols = get_market_universe(name)
        print(f"  {name:18} : {len(symbols):4} symbols")

    print("\n" + "="*70)
    print("💡 RECOMMENDATION: Use 'comprehensive' for daily pre-market discovery")
    print("="*70 + "\n")


if __name__ == '__main__':
    get_universe_info()
