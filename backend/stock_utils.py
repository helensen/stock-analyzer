"""
Utility functions for stock ticker and company name handling
"""

from typing import Optional
from symbols import POPULAR_STOCKS


def normalize_company_name(name: str) -> str:
    """
    Normalize company name for matching
    
    Args:
        name: Company name to normalize
        
    Returns:
        Normalized company name in lowercase without common suffixes
    """
    # Convert to lowercase and strip whitespace
    name = name.lower().strip()
    
    # Remove punctuation
    name = name.replace(',', '').replace('.', '').replace("'", '')
    
    # Remove common company suffixes
    suffixes = [
        ' inc', ' incorporated', ' corp', ' corporation', 
        ' ltd', ' limited', ' llc', ' co', ' company',
        ' group', ' holdings', ' technologies', ' systems',
        ' plc', ' sa', ' ag', ' gmbh', ' the'
    ]
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    
    # Remove "the" from beginning
    if name.startswith('the '):
        name = name[4:].strip()
    
    return name


def find_ticker(search_term: str) -> Optional[str]:
    """
    Convert company name or ticker to ticker symbol
    
    Args:
        search_term: User input (company name or ticker)
        
    Returns:
        Ticker symbol or None if not found
        
    Examples:
        >>> find_ticker("Apple")
        'AAPL'
        >>> find_ticker("AAPL")
        'AAPL'
        >>> find_ticker("Microsoft Corporation")
        'MSFT'
    """
    search_term = search_term.strip()
    
    # If it looks like a ticker (short, uppercase), return as-is
    if len(search_term) <= 5 and search_term.isupper():
        return search_term
    
    # Normalize and search in dictionary
    normalized = normalize_company_name(search_term)
    
    # Direct match
    if normalized in POPULAR_STOCKS:
        return POPULAR_STOCKS[normalized]
    
    # Partial match (for cases like "apple" matching "apple inc")
    for company_name, ticker in POPULAR_STOCKS.items():
        # Check if search term is in company name or vice versa
        if normalized in company_name or company_name in normalized:
            return ticker
    
    # If not found, assume it's a ticker and return uppercase
    return search_term.upper()


def search_companies(query: str, limit: int = 10) -> list:
    """
    Search for companies by partial name or ticker match
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        List of dicts with ticker, name, and display fields
    """
    query_lower = query.lower().strip()
    
    if len(query_lower) < 2:
        return []
    
    matches = []
    seen_tickers = set()
    
    # Search in company names and tickers
    for company_name, ticker in POPULAR_STOCKS.items():
        if ticker in seen_tickers:
            continue
            
        # Check if query matches company name or ticker
        if query_lower in company_name or query_lower in ticker.lower():
            # Format company name nicely (title case)
            display_name = company_name.title()
            
            matches.append({
                'ticker': ticker,
                'name': display_name,
                'display': f"{ticker} - {display_name}"
            })
            
            seen_tickers.add(ticker)
            
            if len(matches) >= limit:
                break
    
    return matches


def is_valid_ticker(ticker: str) -> bool:
    """
    Check if a string looks like a valid ticker symbol
    
    Args:
        ticker: String to validate
        
    Returns:
        True if it looks like a ticker, False otherwise
    """
    ticker = ticker.strip().upper()
    
    # Tickers are typically 1-5 characters, all uppercase letters
    # Can contain dots (e.g., BRK.B) or hyphens
    if not ticker:
        return False
    
    if len(ticker) > 6:
        return False
    
    # Allow letters, dots, and hyphens
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ.-')
    return all(c in allowed_chars for c in ticker)