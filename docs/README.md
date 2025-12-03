# Pipeline de Dados de Cotações de Ações na AWS

## Visão Geral

Este projeto é uma infraestrutura completa na AWS para coletar dados de cotações de ações e informações fundamentais de empresas listadas na bolsa de valores americana. Os dados são coletados da API Alpha Vantage e armazenados no Amazon S3, com execução automática agendada durante o horário comercial da bolsa americana.

### Objetivos Educacionais

- Aprender sobre infraestrutura como código com AWS CloudFormation
- Entender o funcionamento de Lambda Functions e EventBridge
- Trabalhar com APIs externas e armazenamento de dados no S3
- Criar pipelines de dados para análises futuras

## Arquitetura

```
┌─────────────────┐
│  EventBridge    │  (Agendamento: 5 em 5 min, 9:30-16:00 EST)
│     Rule        │
└────────┬────────┘
         │ Invoca
         ▼
┌─────────────────┐
│  Lambda Function│  (Python 3.12)
│  Stock Fetcher   │
└────────┬────────┘
         │ Busca dados
         ▼
┌─────────────────┐
│ Alpha Vantage   │  (API Externa)
│      API        │
└─────────────────┘
         │
         │ Retorna dados
         ▼
┌─────────────────┐
│  Lambda Function│
│  Stock Fetcher   │
└────────┬────────┘
         │ Salva dados
         ▼
┌─────────────────┐
│   S3 Bucket     │
│  stock-quotes-  │
│     data        │
└─────────────────┘
```

### Componentes

1. **Amazon S3**: Armazena dados em formato JSON organizados por tipo e data
2. **AWS Lambda**: Função Python que busca dados da API e salva no S3
3. **Amazon EventBridge**: Agenda execução automática durante horário comercial
4. **IAM Roles**: Permissões necessárias para Lambda acessar S3

## Estrutura de Dados

### Organização no S3

```
s3://{bucket-name}/
├── quotes/
│   └── {YYYY-MM-DD}/
│       └── stock-quotes-{YYYYMMDD-HHMMSS}.json
├── fundamentals/
│   └── {YYYY-MM-DD}/
│       └── company-fundamentals.json
└── company-info/
    └── companies-metadata.json
```

### Formato dos Dados

#### Cotações (`quotes/`)

Arquivos gerados a cada 5 minutos durante o horário comercial.

```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "date": "2024-01-15",
  "quotes": [
    {
      "symbol": "GOOGL",
      "price": 150.25,
      "volume": 1500000,
      "change": 2.5,
      "change_percent": 1.69,
      "high": 151.00,
      "low": 149.50,
      "open": 149.75,
      "timestamp": "2024-01-15 14:30:00"
    }
  ]
}
```

#### Dados Fundamentais (`fundamentals/`)

Arquivo gerado uma vez por dia (primeira execução do dia).

```json
{
  "date": "2024-01-15",
  "companies": [
    {
      "symbol": "GOOGL",
      "market_cap": 1850000000000,
      "pe_ratio": 28.5,
      "dividend_yield": 0.5,
      "roe": 18.2,
      "revenue": 307394000000,
      "net_income": 73795000000,
      "total_assets": 402392000000,
      "sector": "Technology",
      "industry": "Internet Content & Information"
    }
  ]
}
```

#### Metadados de Empresas (`company-info/`)

Arquivo atualizado periodicamente com informações estáticas das empresas.

```json
{
  "last_updated": "2024-01-15",
  "companies": [
    {
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "description": "Alphabet Inc. provides various products...",
      "sector": "Technology",
      "industry": "Internet Content & Information",
      "address": "1600 Amphitheatre Parkway, Mountain View, CA",
      "website": "https://www.abc.xyz",
      "ceo": "Sundar Pichai",
      "ipo_date": "2004-08-19",
      "market_cap_category": "large-cap"
    }
  ]
}
```

## Empresas Monitoradas

### Large-Cap Technology
- **GOOGL** - Alphabet Inc. (Google)
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **AMZN** - Amazon.com Inc.
- **META** - Meta Platforms Inc. (Facebook)
- **TSLA** - Tesla, Inc.
- **NVDA** - NVIDIA Corporation

### Outros Setores
- **JPM** - JPMorgan Chase & Co. (Financeiro)
- **JNJ** - Johnson & Johnson (Saúde)
- **WMT** - Walmart Inc. (Varejo)
- **XOM** - Exxon Mobil Corporation (Energia)

> **Nota**: A lista de empresas pode ser expandida editando o arquivo `lambda/stock_fetcher/company_list.py`

## Como Fazer Deploy

### Método Recomendado: GitHub Actions + AWS SAM

O projeto agora usa **AWS SAM (Serverless Application Model)** e **GitHub Actions** para deploy automatizado, eliminando a necessidade de gerenciar arquivos ZIP manualmente.

#### Pré-requisitos

1. **Conta AWS** com permissões para criar recursos
2. **Repositório GitHub** com o código
3. **AWS Credentials** configuradas como Secrets no GitHub

#### Passo 1: Configurar Credenciais AWS no GitHub

1. Acesse **Settings** → **Secrets and variables** → **Actions** no seu repositório
2. Adicione os seguintes secrets:
   - `AWS_ACCESS_KEY_ID`: Sua AWS Access Key ID
   - `AWS_SECRET_ACCESS_KEY`: Sua AWS Secret Access Key

#### Passo 2: Executar Deploy via GitHub Actions

1. Vá na aba **Actions** do repositório
2. Selecione o workflow **Deploy to AWS**
3. Clique em **Run workflow**
4. Preencha os parâmetros:
   - **Stack name**: `stock-data-pipeline`
   - **AWS Region**: `us-east-1` (ou sua região preferida)
   - **Alpha Vantage API Key**: Sua chave da API
   - **Bucket Name**: `stock-quotes-data`
5. Clique em **Run workflow**

O workflow irá:
- ✅ Fazer build do Lambda automaticamente
- ✅ Instalar dependências do `requirements.txt`
- ✅ Fazer deploy para AWS usando SAM
- ✅ Criar/atualizar todos os recursos necessários

📖 **Documentação completa**: Veja [docs/DEPLOY.md](DEPLOY.md) para instruções detalhadas.

### Método Alternativo: Deploy Local com SAM CLI

Para desenvolvimento e testes locais:

```bash
# Instalar SAM CLI
pip install aws-sam-cli

# Configurar credenciais AWS
aws configure

# Build do projeto
sam build --template template.yaml

# Deploy
sam deploy \
  --stack-name stock-data-pipeline \
  --region us-east-1 \
  --parameter-overrides \
    AlphaVantageApiKey=SUA_API_KEY \
    BucketName=stock-quotes-data \
  --capabilities CAPABILITY_IAM
```

### Método Legado: CloudFormation Manual

O template CloudFormation original ainda está disponível em `infrastructure/cloudformation-template.yaml` para referência, mas não é mais o método recomendado.

## Explicação dos Componentes CloudFormation

### 1. S3 Bucket (`StockDataBucket`)

- **Propósito**: Armazenar todos os dados coletados
- **Configurações**:
  - Versionamento habilitado (mantém histórico)
  - Bloqueio de acesso público
  - Lifecycle policy para transição para Glacier após 90 dias
  - Expiração de versões antigas após 30 dias

### 2. IAM Role (`LambdaExecutionRole`)

- **Propósito**: Dar permissões à Lambda para acessar S3
- **Políticas**:
  - `AWSLambdaBasicExecutionRole`: Permite escrever logs no CloudWatch
  - Policy customizada: Permite `PutObject`, `GetObject` e `ListBucket` no bucket criado

### 3. Lambda Function (`StockFetcherFunction`)

- **Runtime**: Python 3.12
- **Timeout**: 300 segundos (5 minutos)
- **Memory**: 512 MB
- **Variáveis de Ambiente**:
  - `ALPHA_VANTAGE_API_KEY`: Chave da API
  - `S3_BUCKET_NAME`: Nome do bucket S3
- **Handler**: `lambda_function.lambda_handler`

### 4. EventBridge Rule (`StockFetcherSchedule`)

- **Schedule Expression**: `cron(*/5 14-21 ? * MON-FRI *)`
  - Executa a cada 5 minutos
  - Das 14:30 às 21:00 UTC (9:30 AM - 4:00 PM EST)
  - Apenas de segunda a sexta-feira
- **Target**: Lambda Function

### 5. Lambda Permission (`LambdaInvokePermission`)

- **Propósito**: Permitir que EventBridge invoque a Lambda
- **Principal**: `events.amazonaws.com`

## Horário Comercial da Bolsa Americana

- **Horário Local**: 9:30 AM - 4:00 PM EST (Eastern Standard Time)
- **Horário UTC**: 14:30 - 21:00 UTC (durante EST)
- **Dias**: Segunda a Sexta-feira
- **Frequência de Coleta**: A cada 5 minutos

> **Nota**: O horário UTC pode variar durante o horário de verão (EDT). O cron expression atual assume EST. Para ajustar para EDT, use `cron(*/5 13-20 ? * MON-FRI *)`.

## Endpoints Alpha Vantage Utilizados

1. **TIME_SERIES_INTRADAY**: Cotações em tempo real com intervalo de 5 minutos
2. **OVERVIEW**: Dados fundamentais da empresa (capitalização, P/L, setor, etc.)

### Limitações da API

- **Free Tier**: 5 chamadas por minuto, 500 chamadas por dia
- **Premium**: Até 120 chamadas por minuto

> **Dica**: Com 11 empresas e execução a cada 5 minutos, você pode precisar de um plano premium ou ajustar a frequência/quantidade de empresas.

## Exemplos de Análises Possíveis

Com os dados coletados, você pode realizar diversas análises:

### 1. Análise de Correlação
- Correlação entre preços de ações de diferentes empresas
- Identificar empresas que se movem juntas

### 2. Análise Setorial
- Comparar desempenho por setor (Tech vs Financeiro vs Saúde)
- Identificar setores em alta/baixa

### 3. Análise Fundamentalista
- Comparar P/L ratio entre empresas do mesmo setor
- Analisar ROE e dividend yield
- Identificar empresas subvalorizadas

### 4. Análise Técnica
- Calcular médias móveis
- Identificar padrões de volume
- Análise de volatilidade

### 5. Tendências Temporais
- Como os preços variam ao longo do dia
- Padrões de volume durante o dia
- Horários de maior volatilidade

### 6. Market Cap Analysis
- Evolução da capitalização de mercado
- Comparação entre empresas

## Monitoramento e Troubleshooting

### CloudWatch Logs

Todos os logs da Lambda são salvos automaticamente no CloudWatch:

```bash
# Ver logs recentes
aws logs tail /aws/lambda/stock-data-pipeline-StockFetcherFunction-XXXXX --follow
```

### Verificar Execuções

```bash
# Listar execuções recentes
aws lambda list-functions --query 'Functions[?FunctionName==`stock-data-pipeline-StockFetcherFunction-XXXXX`]'

# Ver métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=stock-data-pipeline-StockFetcherFunction-XXXXX \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### Verificar Dados no S3

```bash
# Listar arquivos de cotações
aws s3 ls s3://{bucket-name}/quotes/ --recursive

# Baixar um arquivo para inspecionar
aws s3 cp s3://{bucket-name}/quotes/2024-01-15/stock-quotes-20240115-143000.json ./
```

## Próximos Passos

Este projeto pode ser expandido com:

1. **Amazon DynamoDB**: Armazenar histórico estruturado para consultas rápidas
2. **AWS Glue**: ETL para transformar e preparar dados para análise
3. **Amazon Athena**: Queries SQL diretamente nos dados do S3
4. **Amazon QuickSight**: Dashboards e visualizações interativas
5. **Lambda Adicional**: Processar dados históricos e calcular métricas
6. **API Gateway**: Expor dados via REST API
7. **Amazon SNS**: Notificações quando eventos importantes ocorrem
8. **AWS Step Functions**: Orquestrar múltiplas etapas do pipeline

## Estrutura do Projeto

```
meus-dados/
├── template.yaml                        # Template SAM (deploy principal)
├── .samconfig.toml                      # Configurações SAM
├── infrastructure/
│   └── cloudformation-template.yaml    # Template CloudFormation (legado)
├── .github/
│   └── workflows/
│       └── deploy.yml                  # Workflow GitHub Actions
├── lambda/
│   └── stock-fetcher/
│       ├── lambda_function.py          # Código principal
│       ├── company_list.py             # Lista de empresas
│       └── requirements.txt            # Dependências Python
├── docs/
│   ├── README.md                       # Esta documentação
│   └── DEPLOY.md                       # Guia de deploy detalhado
└── .gitignore                          # Arquivos a ignorar no Git
```

## Segurança

- **API Key**: Armazenada como parâmetro do CloudFormation (não versionada no código)
- **S3 Bucket**: Bloqueio de acesso público habilitado
- **IAM**: Princípio do menor privilégio aplicado
- **Logs**: Não contêm informações sensíveis

## Custos Estimados

### Free Tier (Primeiros 12 meses)
- **Lambda**: 1M requisições gratuitas/mês
- **S3**: 5GB de armazenamento gratuito
- **EventBridge**: 14M eventos gratuitos/mês

### Após Free Tier
- **Lambda**: ~$0.20 por 1M requisições
- **S3**: ~$0.023 por GB/mês
- **EventBridge**: ~$1.00 por 1M eventos

> **Estimativa**: Com execução a cada 5 minutos durante horário comercial (~78 execuções/dia), o custo mensal seria aproximadamente **$2-5 USD**.

## Suporte e Contribuições

Este é um projeto educacional. Para dúvidas ou melhorias:

1. Revise a documentação da AWS CloudFormation
2. Consulte a documentação da Alpha Vantage API
3. Verifique os logs do CloudWatch para troubleshooting

## Licença

Este projeto é para fins educacionais.

