# lambda/stock_fetcher/lambda_function.py
"""
Lambda Function para coletar dados de cotações de ações da Alpha Vantage API
e salvar no Amazon S3 - Versão Produção.
"""

import json
import os
import sys
import boto3
import requests
from datetime import datetime, timezone
import time
import logging
from typing import Dict, List, Any, Optional
import hashlib

# Adicionar diretório atual ao path para importar módulos locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ===== CONFIGURAÇÃO DE LOGGING =====
def setup_logging():
    """Configura logging consistente para AWS e local"""
    logger = logging.getLogger()
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Nível baseado em ambiente
    if os.environ.get('AWS_EXECUTION_ENV'):
        logger.setLevel(logging.INFO)  # Produção
    else:
        logger.setLevel(logging.DEBUG)  # Desenvolvimento
    
    return logger

logger = setup_logging()

# ===== VALIDAÇÃO DE VARIÁVEIS DE AMBIENTE =====
def validate_environment():
    """Valida e obtém variáveis de ambiente críticas"""
    # API Key - OBRIGATÓRIA
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'demo':
        logger.error("❌ ALPHA_VANTAGE_API_KEY não configurada ou está como 'demo'")
        logger.error("Configure a variável de ambiente com sua chave real da Alpha Vantage")
        raise ValueError("ALPHA_VANTAGE_API_KEY é obrigatória")
    
    # Validar formato da API key (Alpha Vantage keys são normalmente 16 caracteres)
    if len(api_key) < 10:
        logger.warning(f"⚠️  API key muito curta: {len(api_key)} caracteres")
    
    # S3 Bucket - OBRIGATÓRIO
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if not bucket_name:
        logger.error("❌ S3_BUCKET_NAME não configurada")
        raise ValueError("S3_BUCKET_NAME é obrigatória")
    
    # Validar nome do bucket (regras S3)
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        logger.error(f"❌ Nome do bucket inválido: deve ter entre 3 e 63 caracteres")
        raise ValueError("Nome do bucket inválido")
    
    # Log seguro
    api_key_display = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
    logger.info(f"✅ API Key: {api_key_display}")
    logger.info(f"✅ S3 Bucket: {bucket_name}")
    
    return api_key, bucket_name

try:
    ALPHA_VANTAGE_API_KEY, S3_BUCKET_NAME = validate_environment()
except ValueError as e:
    logger.critical(f"Falha na validação: {e}")
    logger.critical("Para desenvolvimento local, configure as variáveis:")
    logger.critical("  export ALPHA_VANTAGE_API_KEY='sua_key_real'")
    logger.critical("  export S3_BUCKET_NAME='stock-quotes-data'")
    sys.exit(1)

# ===== INICIALIZAÇÃO DE CLIENTES =====
class AWSClientManager:
    """Gerencia clientes AWS com tratamento de erros"""
    
    @staticmethod
    def get_s3_client():
        """Retorna cliente S3 configurado"""
        try:
            # Para Lambda, usa IAM Role automaticamente
            # Para local, usa credenciais do ~/.aws/credentials
            client = boto3.client('s3')
            
            # Testar conexão (operação leve)
            client.list_buckets()
            logger.info("✅ Cliente S3 inicializado com sucesso")
            return client
        
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar cliente S3: {str(e)}")
            
            # Verificar se é ambiente local
            if not os.environ.get('AWS_EXECUTION_ENV'):
                logger.info("💡 Dica para ambiente local:")
                logger.info("  1. Instale AWS CLI: https://aws.amazon.com/cli/")
                logger.info("  2. Configure: aws configure")
                logger.info("  3. Ou defina AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY")
            
            raise

# Inicializar clientes
try:
    s3_client = AWSClientManager.get_s3_client()
except Exception:
    # Em último caso, criar um cliente básico (pode falhar depois)
    s3_client = boto3.client('s3')
    logger.warning("⚠️  Usando cliente S3 sem validação inicial")

# ===== IMPORTAR LISTA DE EMPRESAS =====
try:
    from company_list import get_all_symbols, COMPANIES
    logger.info(f"✅ Importado company_list com {len(COMPANIES)} empresas")
except ImportError as e:
    logger.critical(f"❌ Falha ao importar company_list: {e}")
    raise

# ===== CLASSE ALPHA VANTAGE API =====
class AlphaVantageAPI:
    """Cliente robusto para Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    RATE_LIMIT_DELAY = 12.1  # 12.1 segundos entre requisições (5/min free tier)
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StockDataPipeline/1.0',
            'Accept': 'application/json'
        })
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Respeita rate limit da API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - time_since_last
            logger.debug(f"Rate limiting: aguardando {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Faz requisição HTTP com tratamento de erros"""
        self._respect_rate_limit()
        
        try:
            logger.debug(f"Request: {params.get('function')} para {params.get('symbol', 'N/A')}")
            
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=30,
                verify=True  # Verificar SSL
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Verificar erros da API
            if "Error Message" in data:
                logger.error(f"API Error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                note = data["Note"]
                if "rate limit" in note.lower():
                    logger.warning(f"⚠️  Rate limit detectado: {note}")
                    # Aumentar delay para próxima requisição
                    self.RATE_LIMIT_DELAY = 60  # 1 minuto
                else:
                    logger.info(f"API Note: {note}")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição (30s)")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text[:100]}")
            return None
        except json.JSONDecodeError:
            logger.error("Resposta não é JSON válido")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return None
    
    def get_intraday_quotes(self, symbol: str) -> Optional[Dict]:
        """Busca cotações intraday (5min interval)"""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "5min",
            "apikey": self.api_key,
            "outputsize": "compact",
            "datatype": "json"
        }
        
        return self._make_request(params)
    
    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Busca dados fundamentais"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        return self._make_request(params)

# ===== PROCESSADOR DE DADOS =====
class StockDataProcessor:
    """Processa e transforma dados brutos"""
    
    @staticmethod
    def extract_latest_quote(api_data: Dict, symbol: str) -> Optional[Dict]:
        """Extrai a cotação mais recente"""
        try:
            time_series = api_data.get("Time Series (5min)", {})
            if not time_series:
                logger.warning(f"Sem dados de série temporal para {symbol}")
                return None
            
            # Encontrar timestamp mais recente
            latest_timestamp = max(time_series.keys())
            quote_data = time_series[latest_timestamp]
            
            # Converter valores
            quote = {
                "symbol": symbol,
                "timestamp": latest_timestamp,
                "price": float(quote_data.get("4. close", 0)),
                "volume": int(quote_data.get("5. volume", 0)),
                "open": float(quote_data.get("1. open", 0)),
                "high": float(quote_data.get("2. high", 0)),
                "low": float(quote_data.get("3. low", 0)),
                "close": float(quote_data.get("4. close", 0))
            }
            
            # Calcular variações
            if quote["open"] > 0:
                quote["change"] = quote["close"] - quote["open"]
                quote["change_percent"] = (quote["change"] / quote["open"]) * 100
            
            # Adicionar metadados da empresa
            company_info = COMPANIES.get(symbol, {})
            quote.update({
                "name": company_info.get("name", ""),
                "sector": company_info.get("sector", ""),
                "industry": company_info.get("industry", "")
            })
            
            logger.debug(f"Processado {symbol}: ${quote['price']:.2f}")
            return quote
            
        except Exception as e:
            logger.error(f"Erro ao processar quote de {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def process_overview_data(api_data: Dict) -> Optional[Dict]:
        """Processa dados fundamentais"""
        try:
            if not api_data or "Symbol" not in api_data:
                return None
            
            processed = {
                "symbol": api_data.get("Symbol"),
                "name": api_data.get("Name", ""),
                "description": (api_data.get("Description", "")[:400] + "...") 
                              if len(api_data.get("Description", "")) > 400 
                              else api_data.get("Description", ""),
                "sector": api_data.get("Sector", ""),
                "industry": api_data.get("Industry", ""),
                "exchange": api_data.get("Exchange", ""),
                "currency": api_data.get("Currency", ""),
                "country": api_data.get("Country", ""),
                "market_cap": StockDataProcessor._safe_float(api_data.get("MarketCapitalization")),
                "pe_ratio": StockDataProcessor._safe_float(api_data.get("PERatio")),
                "dividend_yield": StockDataProcessor._safe_float(api_data.get("DividendYield")),
                "roe": StockDataProcessor._safe_float(api_data.get("ReturnOnEquityTTM")),
                "revenue_ttm": StockDataProcessor._safe_float(api_data.get("RevenueTTM")),
                "gross_profit_ttm": StockDataProcessor._safe_float(api_data.get("GrossProfitTTM")),
                "profit_margin": StockDataProcessor._safe_float(api_data.get("ProfitMargin")),
                "operating_margin": StockDataProcessor._safe_float(api_data.get("OperatingMarginTTM")),
                "eps": StockDataProcessor._safe_float(api_data.get("EPS")),
                "beta": StockDataProcessor._safe_float(api_data.get("Beta")),
                "52_week_high": StockDataProcessor._safe_float(api_data.get("52WeekHigh")),
                "52_week_low": StockDataProcessor._safe_float(api_data.get("52WeekLow")),
                "50_day_moving_avg": StockDataProcessor._safe_float(api_data.get("50DayMovingAverage")),
                "200_day_moving_avg": StockDataProcessor._safe_float(api_data.get("200DayMovingAverage")),
                "shares_outstanding": StockDataProcessor._safe_float(api_data.get("SharesOutstanding")),
                "analyst_target_price": StockDataProcessor._safe_float(api_data.get("AnalystTargetPrice")),
                "analyst_rating": api_data.get("AnalystRating", ""),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Erro ao processar overview: {str(e)}")
            return None
    
    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Converte para float com segurança"""
        if not value or value in ["None", "N/A", "-"]:
            return None
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None

# ===== GERENCIADOR S3 =====
class S3DataManager:
    """Gerencia armazenamento no S3"""
    
    def __init__(self, bucket_name: str, s3_client):
        self.bucket_name = bucket_name
        self.s3_client = s3_client
    
    def save_quotes(self, quotes: List[Dict]) -> bool:
        """Salva cotações no S3"""
        if not quotes:
            logger.warning("Nenhuma cotação para salvar")
            return False
        
        try:
            current_time = datetime.now(timezone.utc)
            date_str = current_time.strftime("%Y-%m-%d")
            timestamp_str = current_time.strftime("%Y%m%d-%H%M%S")
            
            # Estrutura de dados
            data = {
                "metadata": {
                    "pipeline_version": "1.0",
                    "execution_timestamp": current_time.isoformat(),
                    "total_companies": len(quotes),
                    "data_type": "stock_quotes",
                    "source": "alpha_vantage"
                },
                "date": date_str,
                "quotes": quotes
            }
            
            # Gerar hash para integridade
            data_json = json.dumps(data, separators=(',', ':'))
            data_hash = hashlib.md5(data_json.encode()).hexdigest()[:8]
            
            s3_key = f"quotes/{date_str}/stock-quotes-{timestamp_str}-{data_hash}.json"
            
            # Upload para S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data_json,
                ContentType='application/json',
                Metadata={
                    'total-companies': str(len(quotes)),
                    'data-hash': data_hash,
                    'pipeline-version': '1.0'
                }
            )
            
            logger.info(f"✅ Cotações salvas: s3://{self.bucket_name}/{s3_key}")
            logger.info(f"   Empresas: {len(quotes)}, Hash: {data_hash}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha ao salvar cotações: {str(e)}")
            return False
    
    def save_fundamentals(self, fundamentals: List[Dict]) -> bool:
        """Salva dados fundamentais"""
        if not fundamentals:
            return False
        
        try:
            current_time = datetime.now(timezone.utc)
            date_str = current_time.strftime("%Y-%m-%d")
            
            data = {
                "metadata": {
                    "pipeline_version": "1.0",
                    "execution_timestamp": current_time.isoformat(),
                    "total_companies": len(fundamentals),
                    "data_type": "company_fundamentals"
                },
                "date": date_str,
                "companies": fundamentals
            }
            
            s3_key = f"fundamentals/{date_str}/company-fundamentals.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Fundamentais salvas: s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha ao salvar fundamentais: {str(e)}")
            return False

# ===== HANDLER PRINCIPAL =====
def lambda_handler(event, context) -> Dict:
    """
    Handler principal da Lambda Function
    """
    # Início da execução
    start_time = time.time()
    logger.info("🚀 === INICIANDO PIPELINE DE DADOS ===")
    
    # Informações de execução
    if context:
        logger.info(f"Request ID: {context.aws_request_id}")
        logger.info(f"Function: {context.function_name}")
        logger.info(f"Memory: {context.memory_limit_in_mb}MB")
    
    # Inicializar componentes
    api_client = AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)
    processor = StockDataProcessor()
    s3_manager = S3DataManager(S3_BUCKET_NAME, s3_client)
    
    # Obter empresas
    symbols = get_all_symbols()
    logger.info(f"📊 Empresas monitoradas: {len(symbols)}")
    logger.info(f"Símbolos: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    
    # Verificar se deve coletar fundamentais
    current_time = datetime.now(timezone.utc)
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # Coletar fundamentais apenas ~9:30 AM EST (14:30 UTC)
    collect_fundamentals = (current_hour == 14 and current_minute <= 35)
    
    if collect_fundamentals:
        logger.info("⭐ Coletando dados fundamentais (primeira execução do dia)")
    
    # Coletar dados
    successful_quotes = []
    successful_fundamentals = []
    failed_symbols = []
    
    logger.info("🔄 Iniciando coleta de dados...")
    
    for idx, symbol in enumerate(symbols, 1):
        try:
            logger.info(f"[{idx}/{len(symbols)}] Processando {symbol}")
            
            # 1. Coletar cotações
            quote_data = api_client.get_intraday_quotes(symbol)
            
            if quote_data:
                quote = processor.extract_latest_quote(quote_data, symbol)
                if quote:
                    successful_quotes.append(quote)
                    
                    # Log resumido
                    change_str = f"Δ {quote.get('change_percent', 0):+.2f}%"
                    logger.info(f"   ✓ ${quote['price']:.2f} ({change_str})")
                else:
                    failed_symbols.append(symbol)
                    logger.warning(f"   ✗ Sem dados de cotação")
            else:
                failed_symbols.append(symbol)
                logger.warning(f"   ✗ Falha na API")
            
            # 2. Coletar fundamentais (se for hora)
            if collect_fundamentals:
                overview_data = api_client.get_company_overview(symbol)
                if overview_data:
                    fundamentals = processor.process_overview_data(overview_data)
                    if fundamentals:
                        successful_fundamentals.append(fundamentals)
                        logger.info(f"   ✓ Fundamentais coletados")
            
            # Progresso
            if idx % 5 == 0:
                progress = (idx / len(symbols)) * 100
                logger.info(f"📈 Progresso: {progress:.1f}% ({idx}/{len(symbols)})")
                
        except Exception as e:
            failed_symbols.append(symbol)
            logger.error(f"   💥 Erro inesperado em {symbol}: {str(e)}")
            continue
    
    # Salvar dados
    save_results = {
        "quotes_saved": False,
        "fundamentals_saved": False
    }
    
    # Salvar cotações
    if successful_quotes:
        save_results["quotes_saved"] = s3_manager.save_quotes(successful_quotes)
    
    # Salvar fundamentais
    if successful_fundamentals and collect_fundamentals:
        save_results["fundamentals_saved"] = s3_manager.save_fundamentals(successful_fundamentals)
    
    # Resumo da execução
    execution_time = time.time() - start_time
    logger.info("=" * 50)
    logger.info("🎯 === RESUMO DA EXECUÇÃO ===")
    logger.info(f"✅ Sucessos: {len(successful_quotes)}/{len(symbols)} cotações")
    logger.info(f"✅ Fundamentais: {len(successful_fundamentals)} coletados")
    
    if failed_symbols:
        logger.warning(f"⚠️  Falhas: {len(failed_symbols)} símbolos")
        logger.debug(f"Símbolos com falha: {failed_symbols}")
    
    logger.info(f"💾 S3 Quotes: {'✓' if save_results['quotes_saved'] else '✗'}")
    logger.info(f"💾 S3 Fundamentais: {'✓' if save_results['fundamentals_saved'] else '✗'}")
    logger.info(f"⏱️  Tempo total: {execution_time:.1f} segundos")
    logger.info("=" * 50)
    
    # Retorno para Lambda
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'completed',
            'execution_time_seconds': round(execution_time, 2),
            'companies_total': len(symbols),
            'quotes_successful': len(successful_quotes),
            'fundamentals_successful': len(successful_fundamentals),
            'failed_symbols': failed_symbols,
            's3_save_results': save_results,
            'timestamp': current_time.isoformat()
        })
    }

# ===== CÓDIGO PARA TESTE LOCAL =====
if __name__ == "__main__":
    """
    Teste local da Lambda Function
    """
    print("=" * 60)
    print("🧪 TESTE LOCAL - PIPELINE DE DADOS DE AÇÕES")
    print("=" * 60)
    
    # Verificar configuração
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == 'demo':
        print("\n❌ ERRO: API KEY não configurada!")
        print("\nConfigure a variável de ambiente:")
        print("  Windows (PowerShell):")
        print("    $env:ALPHA_VANTAGE_API_KEY='IRYWV66KYDTB6S2W'")
        print("    $env:S3_BUCKET_NAME='stock-quotes-data'")
        print("\n  Linux/Mac:")
        print("    export ALPHA_VANTAGE_API_KEY='IRYWV66KYDTB6S2W'")
        print("    export S3_BUCKET_NAME='stock-quotes-data'")
        print("\n  Ou crie um arquivo .env na raiz do projeto:")
        print("    ALPHA_VANTAGE_API_KEY=IRYWV66KYDTB6S2W")
        print("    S3_BUCKET_NAME=stock-quotes-data")
        sys.exit(1)
    
    print(f"\n✅ Configuração validada:")
    print(f"   API Key: {ALPHA_VANTAGE_API_KEY[:8]}...{ALPHA_VANTAGE_API_KEY[-4:]}")
    print(f"   S3 Bucket: {S3_BUCKET_NAME}")
    print(f"   Empresas: {len(get_all_symbols())}")
    
    # Mock context
    class MockContext:
        aws_request_id = f"local-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        function_name = "stock-data-pipeline-local"
        memory_limit_in_mb = "512"
        function_version = "$LATEST"
    
    print("\n" + "=" * 60)
    print("🚀 Iniciando execução local...")
    print("=" * 60)
    
    try:
        # Executar
        result = lambda_handler({}, MockContext())
        
        print("\n✅ Execução local concluída!")
        print("\n📊 Resultados:")
        
        body = json.loads(result['body'])
        print(f"   Status: {body.get('status', 'unknown')}")
        print(f"   Tempo: {body.get('execution_time_seconds', 0):.1f}s")
        print(f"   Cotações: {body.get('quotes_successful', 0)}/{body.get('companies_total', 0)}")
        print(f"   Fundamentais: {body.get('fundamentals_successful', 0)}")
        
        if body.get('failed_symbols'):
            print(f"   Falhas: {len(body['failed_symbols'])} símbolos")
            print(f"   Lista: {body['failed_symbols']}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO durante execução: {str(e)}")
        import traceback
        traceback.print_exc()