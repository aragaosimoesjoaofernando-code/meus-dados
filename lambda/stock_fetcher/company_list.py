"""
Lista de empresas para monitorar com seus metadados.
Esta lista pode ser expandida conforme necessário.
"""

# Lista de empresas organizadas por categoria
COMPANIES = {
    # Large-Cap Technology
    'GOOGL': {
        'name': 'Alphabet Inc.',
        'sector': 'Technology',
        'industry': 'Internet Content & Information',
        'market_cap_category': 'large-cap'
    },
    'AAPL': {
        'name': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'market_cap_category': 'large-cap'
    },
    'MSFT': {
        'name': 'Microsoft Corporation',
        'sector': 'Technology',
        'industry': 'Software—Infrastructure',
        'market_cap_category': 'large-cap'
    },
    'AMZN': {
        'name': 'Amazon.com Inc.',
        'sector': 'Consumer Cyclical',
        'industry': 'Internet Retail',
        'market_cap_category': 'large-cap'
    },
    'META': {
        'name': 'Meta Platforms Inc.',
        'sector': 'Technology',
        'industry': 'Internet Content & Information',
        'market_cap_category': 'large-cap'
    },
    'TSLA': {
        'name': 'Tesla, Inc.',
        'sector': 'Consumer Cyclical',
        'industry': 'Auto Manufacturers',
        'market_cap_category': 'large-cap'
    },
    'NVDA': {
        'name': 'NVIDIA Corporation',
        'sector': 'Technology',
        'industry': 'Semiconductors',
        'market_cap_category': 'large-cap'
    },
    # Financial Sector
    'JPM': {
        'name': 'JPMorgan Chase & Co.',
        'sector': 'Financial Services',
        'industry': 'Banks—Diversified',
        'market_cap_category': 'large-cap'
    },
    # Healthcare Sector
    'JNJ': {
        'name': 'Johnson & Johnson',
        'sector': 'Healthcare',
        'industry': 'Drug Manufacturers—General',
        'market_cap_category': 'large-cap'
    },
    # Consumer Defensive
    'WMT': {
        'name': 'Walmart Inc.',
        'sector': 'Consumer Defensive',
        'industry': 'Discount Stores',
        'market_cap_category': 'large-cap'
    },
    # Energy Sector
    'XOM': {
        'name': 'Exxon Mobil Corporation',
        'sector': 'Energy',
        'industry': 'Oil & Gas Integrated',
        'market_cap_category': 'large-cap'
    }
}

def get_all_symbols():
    """Retorna lista de todos os símbolos das ações."""
    return list(COMPANIES.keys())

def get_company_info(symbol):
    """Retorna informações de uma empresa específica."""
    return COMPANIES.get(symbol.upper())

def get_companies_by_sector(sector):
    """Retorna empresas filtradas por setor."""
    return {symbol: info for symbol, info in COMPANIES.items() 
            if info['sector'] == sector}

def get_companies_by_category(category):
    """Retorna empresas filtradas por categoria de capitalização."""
    return {symbol: info for symbol, info in COMPANIES.items() 
            if info['market_cap_category'] == category}

