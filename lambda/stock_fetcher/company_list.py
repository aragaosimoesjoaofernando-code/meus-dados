"""
Lista de empresas para monitorar com seus metadados.
Esta lista pode ser expandida conforme necessário.
"""

# Lista de empresas organizadas por categoria
COMPANIES = {
    # ============ Large-Cap Technology ============
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
    'ADBE': {
        'name': 'Adobe Inc.',
        'sector': 'Technology',
        'industry': 'Software—Infrastructure',
        'market_cap_category': 'large-cap'
    },
    'INTC': {
        'name': 'Intel Corporation',
        'sector': 'Technology',
        'industry': 'Semiconductors',
        'market_cap_category': 'large-cap'
    },

    # ============ Financial Sector ============
    'JPM': {
        'name': 'JPMorgan Chase & Co.',
        'sector': 'Financial Services',
        'industry': 'Banks—Diversified',
        'market_cap_category': 'large-cap'
    },
    'BAC': {
        'name': 'Bank of America Corporation',
        'sector': 'Financial Services',
        'industry': 'Banks—Diversified',
        'market_cap_category': 'large-cap'
    },
    'WFC': {
        'name': 'Wells Fargo & Company',
        'sector': 'Financial Services',
        'industry': 'Banks—Diversified',
        'market_cap_category': 'large-cap'
    },
    'GS': {
        'name': 'The Goldman Sachs Group, Inc.',
        'sector': 'Financial Services',
        'industry': 'Capital Markets',
        'market_cap_category': 'large-cap'
    },
    'V': {
        'name': 'Visa Inc.',
        'sector': 'Financial Services',
        'industry': 'Credit Services',
        'market_cap_category': 'large-cap'
    },
    'MA': {
        'name': 'Mastercard Incorporated',
        'sector': 'Financial Services',
        'industry': 'Credit Services',
        'market_cap_category': 'large-cap'
    },

    # ============ Healthcare Sector ============
    'JNJ': {
        'name': 'Johnson & Johnson',
        'sector': 'Healthcare',
        'industry': 'Drug Manufacturers—General',
        'market_cap_category': 'large-cap'
    },
    'PFE': {
        'name': 'Pfizer Inc.',
        'sector': 'Healthcare',
        'industry': 'Drug Manufacturers—General',
        'market_cap_category': 'large-cap'
    },
    'MRK': {
        'name': 'Merck & Co., Inc.',
        'sector': 'Healthcare',
        'industry': 'Drug Manufacturers—General',
        'market_cap_category': 'large-cap'
    },
    'UNH': {
        'name': 'UnitedHealth Group Incorporated',
        'sector': 'Healthcare',
        'industry': 'Healthcare Plans',
        'market_cap_category': 'large-cap'
    },
    'ABT': {
        'name': 'Abbott Laboratories',
        'sector': 'Healthcare',
        'industry': 'Medical Devices',
        'market_cap_category': 'large-cap'
    },
    'TMO': {
        'name': 'Thermo Fisher Scientific Inc.',
        'sector': 'Healthcare',
        'industry': 'Diagnostics & Research',
        'market_cap_category': 'large-cap'
    },

    # ============ Consumer Defensive ============
    'WMT': {
        'name': 'Walmart Inc.',
        'sector': 'Consumer Defensive',
        'industry': 'Discount Stores',
        'market_cap_category': 'large-cap'
    },
    'PG': {
        'name': 'The Procter & Gamble Company',
        'sector': 'Consumer Defensive',
        'industry': 'Household & Personal Products',
        'market_cap_category': 'large-cap'
    },
    'KO': {
        'name': 'The Coca-Cola Company',
        'sector': 'Consumer Defensive',
        'industry': 'Beverages—Non-Alcoholic',
        'market_cap_category': 'large-cap'
    },
    'PEP': {
        'name': 'PepsiCo, Inc.',
        'sector': 'Consumer Defensive',
        'industry': 'Beverages—Non-Alcoholic',
        'market_cap_category': 'large-cap'
    },
    'COST': {
        'name': 'Costco Wholesale Corporation',
        'sector': 'Consumer Defensive',
        'industry': 'Discount Stores',
        'market_cap_category': 'large-cap'
    },

    # ============ Energy Sector ============
    'XOM': {
        'name': 'Exxon Mobil Corporation',
        'sector': 'Energy',
        'industry': 'Oil & Gas Integrated',
        'market_cap_category': 'large-cap'
    },
    'CVX': {
        'name': 'Chevron Corporation',
        'sector': 'Energy',
        'industry': 'Oil & Gas Integrated',
        'market_cap_category': 'large-cap'
    },
    'COP': {
        'name': 'ConocoPhillips',
        'sector': 'Energy',
        'industry': 'Oil & Gas E&P',
        'market_cap_category': 'large-cap'
    },
    'SLB': {
        'name': 'Schlumberger Limited',
        'sector': 'Energy',
        'industry': 'Oil & Gas Equipment & Services',
        'market_cap_category': 'large-cap'
    },

    # ============ Industrial Sector ============
    'BA': {
        'name': 'The Boeing Company',
        'sector': 'Industrials',
        'industry': 'Aerospace & Defense',
        'market_cap_category': 'large-cap'
    },
    'CAT': {
        'name': 'Caterpillar Inc.',
        'sector': 'Industrials',
        'industry': 'Farm & Heavy Construction Machinery',
        'market_cap_category': 'large-cap'
    },
    'HON': {
        'name': 'Honeywell International Inc.',
        'sector': 'Industrials',
        'industry': 'Conglomerates',
        'market_cap_category': 'large-cap'
    },
    'UPS': {
        'name': 'United Parcel Service, Inc.',
        'sector': 'Industrials',
        'industry': 'Integrated Freight & Logistics',
        'market_cap_category': 'large-cap'
    },

    # ============ Communication Services ============
    'DIS': {
        'name': 'The Walt Disney Company',
        'sector': 'Communication Services',
        'industry': 'Entertainment',
        'market_cap_category': 'large-cap'
    },
    'NFLX': {
        'name': 'Netflix, Inc.',
        'sector': 'Communication Services',
        'industry': 'Entertainment',
        'market_cap_category': 'large-cap'
    },
    'CMCSA': {
        'name': 'Comcast Corporation',
        'sector': 'Communication Services',
        'industry': 'Telecom Services',
        'market_cap_category': 'large-cap'
    },
    'TMUS': {
        'name': 'T-Mobile US, Inc.',
        'sector': 'Communication Services',
        'industry': 'Telecom Services',
        'market_cap_category': 'large-cap'
    },

    # ============ Real Estate ============
    'AMT': {
        'name': 'American Tower Corporation',
        'sector': 'Real Estate',
        'industry': 'REIT—Specialty',
        'market_cap_category': 'large-cap'
    },
    'PLD': {
        'name': 'Prologis, Inc.',
        'sector': 'Real Estate',
        'industry': 'REIT—Industrial',
        'market_cap_category': 'large-cap'
    },

    # ============ Utilities ============
    'NEE': {
        'name': 'NextEra Energy, Inc.',
        'sector': 'Utilities',
        'industry': 'Utilities—Renewable',
        'market_cap_category': 'large-cap'
    },
    'DUK': {
        'name': 'Duke Energy Corporation',
        'sector': 'Utilities',
        'industry': 'Utilities—Regulated Electric',
        'market_cap_category': 'large-cap'
    },

    # ============ Materials ============
    'LIN': {
        'name': 'Linde plc',
        'sector': 'Materials',
        'industry': 'Specialty Chemicals',
        'market_cap_category': 'large-cap'
    },
    'APD': {
        'name': 'Air Products and Chemicals, Inc.',
        'sector': 'Materials',
        'industry': 'Specialty Chemicals',
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


def get_sector_distribution():
    """Retorna distribuição de empresas por setor."""
    distribution = {}
    for symbol, info in COMPANIES.items():
        sector = info['sector']
        distribution[sector] = distribution.get(sector, 0) + 1
    return distribution


if __name__ == "__main__":
    # Teste das funções
    print(f"Total de empresas: {len(get_all_symbols())}")
    print(f"Setores: {get_sector_distribution()}")

    # Exemplo de empresas por setor
    tech_companies = get_companies_by_sector('Technology')
    print(f"\nEmpresas de Tecnologia: {len(tech_companies)}")
    print(f"Símbolos: {list(tech_companies.keys())}")
