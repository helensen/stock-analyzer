"""
Stock symbols dictionary
Maps company names to their ticker symbols
"""

POPULAR_STOCKS = {
    # Tech Giants
    'apple': 'AAPL',
    'apple inc': 'AAPL',
    'microsoft': 'MSFT',
    'microsoft corporation': 'MSFT',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'alphabet inc': 'GOOGL',
    'amazon': 'AMZN',
    'amazon.com': 'AMZN',
    'amazon com': 'AMZN',
    'tesla': 'TSLA',
    'tesla inc': 'TSLA',
    'meta': 'META',
    'meta platforms': 'META',
    'facebook': 'META',
    'nvidia': 'NVDA',
    'netflix': 'NFLX',
    'adobe': 'ADBE',
    'salesforce': 'CRM',
    'oracle': 'ORCL',
    'intel': 'INTC',
    'intel corporation': 'INTC',
    'amd': 'AMD',
    'advanced micro devices': 'AMD',
    'qualcomm': 'QCOM',
    'cisco': 'CSCO',
    'cisco systems': 'CSCO',
    'ibm': 'IBM',
    'international business machines': 'IBM',
    
    # Social Media & Communication
    'spotify': 'SPOT',
    'snap': 'SNAP',
    'snapchat': 'SNAP',
    'twitter': 'TWTR',
    'x': 'TWTR',
    'zoom': 'ZM',
    'slack': 'WORK',
    'pinterest': 'PINS',
    'reddit': 'RDDT',
    
    # E-commerce & Fintech
    'shopify': 'SHOP',
    'square': 'SQ',
    'block': 'SQ',
    'paypal': 'PYPL',
    'coinbase': 'COIN',
    'stripe': 'STRIPE',
    'robinhood': 'HOOD',
    'sofi': 'SOFI',
    
    # Transportation & Travel
    'uber': 'UBER',
    'uber technologies': 'UBER',
    'lyft': 'LYFT',
    'airbnb': 'ABNB',
    'doordash': 'DASH',
    'booking': 'BKNG',
    'booking holdings': 'BKNG',
    'expedia': 'EXPE',
    
    # Finance & Banking
    'jpmorgan': 'JPM',
    'jp morgan': 'JPM',
    'jpmorgan chase': 'JPM',
    'bank of america': 'BAC',
    'wells fargo': 'WFC',
    'goldman sachs': 'GS',
    'morgan stanley': 'MS',
    'citigroup': 'C',
    'citi': 'C',
    'visa': 'V',
    'mastercard': 'MA',
    'american express': 'AXP',
    'amex': 'AXP',
    'charles schwab': 'SCHW',
    'schwab': 'SCHW',
    
    # Retail & Consumer
    'walmart': 'WMT',
    'target': 'TGT',
    'costco': 'COST',
    'home depot': 'HD',
    'the home depot': 'HD',
    "lowe's": 'LOW',
    'lowes': 'LOW',
    'nike': 'NKE',
    'starbucks': 'SBUX',
    'mcdonalds': 'MCD',
    "mcdonald's": 'MCD',
    'chipotle': 'CMG',
    'coca cola': 'KO',
    'coca-cola': 'KO',
    'pepsi': 'PEP',
    'pepsico': 'PEP',
    'procter & gamble': 'PG',
    'procter and gamble': 'PG',
    'pg': 'PG',
    
    # Healthcare & Pharma
    'johnson & johnson': 'JNJ',
    'johnson and johnson': 'JNJ',
    'jnj': 'JNJ',
    'pfizer': 'PFE',
    'moderna': 'MRNA',
    'abbvie': 'ABBV',
    'merck': 'MRK',
    'bristol myers': 'BMY',
    'bristol-myers squibb': 'BMY',
    'eli lilly': 'LLY',
    'lilly': 'LLY',
    'unitedhealth': 'UNH',
    'cvs': 'CVS',
    'cvs health': 'CVS',
    'walgreens': 'WBA',
    
    # Energy
    'exxon': 'XOM',
    'exxonmobil': 'XOM',
    'exxon mobil': 'XOM',
    'chevron': 'CVX',
    'conocophillips': 'COP',
    'shell': 'SHEL',
    'bp': 'BP',
    'british petroleum': 'BP',
    
    # Industrial & Manufacturing
    'boeing': 'BA',
    '3m': 'MMM',
    'caterpillar': 'CAT',
    'general electric': 'GE',
    'ge': 'GE',
    'lockheed martin': 'LMT',
    'raytheon': 'RTX',
    'raytheon technologies': 'RTX',
    'deere': 'DE',
    'john deere': 'DE',
    'honeywell': 'HON',
    
    # Automotive
    'ford': 'F',
    'ford motor': 'F',
    'general motors': 'GM',
    'gm': 'GM',
    'toyota': 'TM',
    'honda': 'HMC',
    'ferrari': 'RACE',
    'rivian': 'RIVN',
    'lucid': 'LCID',
    'lucid motors': 'LCID',
    'nikola': 'NKLA',
    
    # Media & Entertainment
    'disney': 'DIS',
    'walt disney': 'DIS',
    'the walt disney company': 'DIS',
    'comcast': 'CMCSA',
    'warner bros': 'WBD',
    'paramount': 'PARA',
    'sony': 'SONY',
    'electronic arts': 'EA',
    'ea': 'EA',
    'activision': 'ATVI',
    'take two': 'TTWO',
    'roblox': 'RBLX',
    
    # Semiconductors
    'taiwan semiconductor': 'TSM',
    'tsmc': 'TSM',
    'asml': 'ASML',
    'broadcom': 'AVGO',
    'texas instruments': 'TXN',
    'micron': 'MU',
    'micron technology': 'MU',
    
    # Telecom
    'at&t': 'T',
    'att': 'T',
    'verizon': 'VZ',
    't-mobile': 'TMUS',
    'tmobile': 'TMUS',
    't mobile': 'TMUS',
    
    # Other Major Companies
    'berkshire hathaway': 'BRK.B',
    'berkshire': 'BRK.B',
    'fedex': 'FDX',
    'ups': 'UPS',
    'united parcel service': 'UPS',
    'marriott': 'MAR',
    'hilton': 'HLT',
    'delta': 'DAL',
    'delta air lines': 'DAL',
    'american airlines': 'AAL',
    'united airlines': 'UAL',
    'southwest': 'LUV',
    'southwest airlines': 'LUV',
}

def get_all_tickers():
    """Return unique list of all ticker symbols"""
    return list(set(POPULAR_STOCKS.values()))

def get_companies_by_ticker(ticker):
    """Return all company name variations for a given ticker"""
    ticker = ticker.upper()
    return [name for name, tick in POPULAR_STOCKS.items() if tick == ticker]