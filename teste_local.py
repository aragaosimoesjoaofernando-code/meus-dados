# test_local.py na raiz do projeto
"""
Script para testar rapidamente a função Lambda localmente
"""

import os
import sys
import json
from datetime import datetime

# Configurar variáveis de ambiente
os.environ['ALPHA_VANTAGE_API_KEY'] = 'IRYWV66KYDTB6S2W'  # SUA KEY REAL
os.environ['S3_BUCKET_NAME'] = 'stock-quotes-data'       # SEU BUCKET REAL

# Adicionar path
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), 'lambda', 'stock_fetcher'))

print("🔧 Importando função Lambda...")
try:
    from lambda_function import lambda_handler
    print("✅ Função importada com sucesso!")
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# Contexto de teste


class TestContext:
    aws_request_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    function_name = "stock-fetcher-test"
    memory_limit_in_mb = "512"


# Executar
print("\n🚀 Executando função Lambda...")
try:
    result = lambda_handler({}, TestContext())

    print("\n📊 RESULTADOS:")
    print("-" * 40)

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"✅ Status: Sucesso")
        print(f"📈 Cotações coletadas: {body.get('quotes_successful', 0)}")
        print(f"🏢 Fundamentais: {body.get('fundamentals_successful', 0)}")
        print(f"⏱️  Tempo: {body.get('execution_time_seconds', 0):.1f}s")
        print(f"🕐 Timestamp: {body.get('timestamp', 'N/A')}")
    else:
        print(f"❌ Status Code: {result['statusCode']}")
        print(f"📝 Body: {result['body']}")

except Exception as e:
    print(f"\n💥 ERRO: {str(e)}")
print("\n🏁 Execução finalizada.")

