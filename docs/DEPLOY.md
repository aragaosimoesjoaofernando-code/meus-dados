# Guia de Deploy - GitHub Actions e AWS SAM

Este guia explica como fazer deploy da infraestrutura usando GitHub Actions e AWS SAM, eliminando a necessidade de gerenciar arquivos ZIP manualmente.

## Visão Geral

O projeto foi migrado para usar **AWS SAM (Serverless Application Model)**, que:
- Gerencia automaticamente o build e packaging do Lambda
- Instala dependências do `requirements.txt` automaticamente
- Faz upload do código para S3 durante o deploy
- Simplifica o processo de atualização do código

## Pré-requisitos

### 1. Conta AWS
- Conta AWS ativa com permissões para criar recursos
- Acesso para criar IAM roles, Lambda functions, S3 buckets e EventBridge rules

### 2. GitHub Repository
- Repositório no GitHub com o código do projeto
- Acesso para configurar Secrets e executar Actions

### 3. AWS SAM CLI (Opcional - para testes locais)
```bash
# Instalar SAM CLI
pip install aws-sam-cli

# Verificar instalação
sam --version
```

## Configuração Inicial

### Passo 1: Configurar AWS Credentials no GitHub

Você precisa configurar as credenciais AWS como Secrets no GitHub:

1. Acesse seu repositório no GitHub
2. Vá em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

#### Secret 1: `AWS_ACCESS_KEY_ID`
- **Name**: `AWS_ACCESS_KEY_ID`
- **Value**: Sua AWS Access Key ID
- Como obter:
  ```bash
  # Via AWS Console
  # IAM → Users → Seu usuário → Security credentials → Create access key
  ```

#### Secret 2: `AWS_SECRET_ACCESS_KEY`
- **Name**: `AWS_SECRET_ACCESS_KEY`
- **Value**: Sua AWS Secret Access Key
- ⚠️ **IMPORTANTE**: Mantenha esta chave segura e nunca a compartilhe

#### Alternativa: Usar OIDC (Recomendado para Produção)

Para maior segurança, você pode usar OIDC ao invés de access keys:

1. Configure OIDC provider na AWS
2. Crie uma IAM Role com trust policy para GitHub
3. Atualize o workflow para usar `aws-actions/configure-aws-credentials@v4` com `role-to-assume`

### Passo 2: Verificar Estrutura do Projeto

Certifique-se de que a estrutura do projeto está correta:

```
meus-dados/
├── template.yaml              # Template SAM
├── .samconfig.toml            # Configurações SAM (opcional)
├── .github/
│   └── workflows/
│       └── deploy.yml         # Workflow GitHub Actions
└── lambda/
    └── stock-fetcher/
        ├── lambda_function.py
        ├── company_list.py
        └── requirements.txt
```

## Deploy via GitHub Actions

### Executar Deploy Manualmente

1. Acesse seu repositório no GitHub
2. Vá na aba **Actions**
3. Selecione o workflow **Deploy to AWS**
4. Clique em **Run workflow**
5. Preencha os parâmetros:
   - **Stack name**: Nome do CloudFormation stack (ex: `stock-data-pipeline`)
   - **AWS Region**: Região onde fazer deploy (ex: `us-east-1`)
   - **Alpha Vantage API Key**: Sua chave da API Alpha Vantage
   - **Bucket Name**: Nome base do bucket S3 (ex: `stock-quotes-data`)
6. Clique em **Run workflow**

### Parâmetros do Workflow

| Parâmetro | Descrição | Padrão | Obrigatório |
|-----------|-----------|--------|-------------|
| `stack_name` | Nome do CloudFormation stack | `stock-data-pipeline` | Sim |
| `aws_region` | Região AWS | `us-east-1` | Sim |
| `alpha_vantage_api_key` | Chave da API Alpha Vantage | - | Sim |
| `bucket_name` | Nome base do bucket S3 | `stock-quotes-data` | Não |

### Monitorar o Deploy

Durante a execução do workflow, você pode:
- Ver os logs em tempo real na aba **Actions**
- Verificar cada step do processo
- Identificar erros rapidamente

O workflow executa os seguintes passos:
1. ✅ Checkout do código
2. ✅ Setup Python 3.12
3. ✅ Instalação do AWS SAM CLI
4. ✅ Configuração de credenciais AWS
5. ✅ Build do Lambda (`sam build`)
6. ✅ Deploy para AWS (`sam deploy`)

## Deploy Local (Desenvolvimento)

Para testar o deploy localmente antes de usar GitHub Actions:

### 1. Configurar Credenciais AWS Localmente

```bash
# Via AWS CLI
aws configure

# Ou definir variáveis de ambiente
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. Build do Projeto

```bash
# Navegar para o diretório do projeto
cd meus-dados

# Build do Lambda (instala dependências automaticamente)
sam build --template template.yaml
```

Isso irá:
- Instalar dependências do `requirements.txt` em `.aws-sam/build/`
- Preparar o código para deploy

### 3. Deploy Local

```bash
# Deploy usando configurações do .samconfig.toml
sam deploy

# Ou com parâmetros customizados
sam deploy \
  --stack-name stock-data-pipeline \
  --region us-east-1 \
  --parameter-overrides \
    AlphaVantageApiKey=SUA_API_KEY \
    BucketName=stock-quotes-data \
  --capabilities CAPABILITY_IAM
```

### 4. Verificar Deploy

```bash
# Ver status do stack
aws cloudformation describe-stacks --stack-name stock-data-pipeline

# Ver outputs
aws cloudformation describe-stacks \
  --stack-name stock-data-pipeline \
  --query 'Stacks[0].Outputs'
```

## Atualizar Código Lambda

### Via GitHub Actions (Recomendado)

1. Faça alterações no código em `lambda/stock-fetcher/`
2. Commit e push para o repositório
3. Execute o workflow **Deploy to AWS** novamente
4. O SAM irá detectar mudanças e atualizar apenas o Lambda

### Via Local

```bash
# Após fazer alterações
sam build --template template.yaml
sam deploy
```

## Estrutura do Template SAM

O arquivo `template.yaml` usa a sintaxe SAM que é uma extensão do CloudFormation:

```yaml
Transform: AWS::Serverless-2016-10-31

Resources:
  StockFetcherFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: lambda/stock-fetcher/  # SAM detecta requirements.txt aqui
      Handler: lambda_function.lambda_handler
      Runtime: python3.12
```

### Diferenças do CloudFormation Original

- ✅ Não precisa especificar `S3Bucket` e `S3Key` manualmente
- ✅ SAM gerencia o packaging automaticamente
- ✅ Dependências do `requirements.txt` são instaladas automaticamente
- ✅ EventBridge schedule pode ser definido diretamente no `Events`

## Troubleshooting

### Erro: "AWS credentials not found"

**Solução**: Verifique se os secrets `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` estão configurados no GitHub.

### Erro: "Stack already exists"

**Solução**: O stack já existe. O SAM irá fazer update. Se quiser criar novo, use um nome diferente ou delete o stack existente:
```bash
aws cloudformation delete-stack --stack-name stock-data-pipeline
```

### Erro: "Unable to upload artifact"

**Solução**: Verifique permissões IAM. O usuário precisa de:
- `s3:PutObject`
- `s3:GetObject`
- `s3:CreateBucket` (se o bucket SAM não existir)

### Erro: "Requirements installation failed"

**Solução**: Verifique o arquivo `requirements.txt` e se todas as dependências são válidas:
```bash
# Testar localmente
cd lambda/stock-fetcher
pip install -r requirements.txt
```

### Build Local Funciona, mas GitHub Actions Falha

**Possíveis causas**:
1. Versão do Python diferente (workflow usa 3.12)
2. Dependências com binários específicos de plataforma
3. Timeout durante instalação de dependências

**Solução**: Verifique os logs do GitHub Actions para identificar o erro específico.

## Configuração Avançada

### Customizar .samconfig.toml

O arquivo `.samconfig.toml` permite definir configurações padrão:

```toml
[default.deploy.parameters]
region = "us-east-1"
stack_name = "stock-data-pipeline"
capabilities = "CAPABILITY_IAM"
parameter_overrides = [
    "AlphaVantageApiKey=SUA_KEY",
    "BucketName=stock-quotes-data"
]
```

### Usar Diferentes Ambientes

Você pode criar múltiplos perfis no `.samconfig.toml`:

```toml
[dev]
[dev.deploy.parameters]
stack_name = "stock-data-pipeline-dev"

[prod]
[prod.deploy.parameters]
stack_name = "stock-data-pipeline-prod"
```

E usar com:
```bash
sam deploy --config-env dev
```

## Segurança

### Boas Práticas

1. **Nunca commite credenciais**: Use GitHub Secrets
2. **Use OIDC quando possível**: Mais seguro que access keys
3. **Princípio do menor privilégio**: IAM roles com apenas permissões necessárias
4. **Rotacione credenciais**: Mude access keys periodicamente
5. **Monitore custos**: Configure billing alerts na AWS

### Rotacionar Credenciais AWS

1. Criar nova access key na AWS Console
2. Atualizar secrets no GitHub
3. Testar deploy
4. Deletar access key antiga

## Próximos Passos

Após o deploy bem-sucedido:

1. ✅ Verificar logs do Lambda no CloudWatch
2. ✅ Testar execução manual da Lambda
3. ✅ Verificar dados sendo salvos no S3
4. ✅ Configurar alertas no CloudWatch
5. ✅ Monitorar custos na AWS

## Referências

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SAM CLI Reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

