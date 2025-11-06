Python

import pandas as pd
import matplotlib.pyplot as plt    
import numpy as np
import seaborn as sns

#Configurar o estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


#Exibir todas as colunas no pandas
pd.set_option('display.max_columns', None)

# Exemplo 1: Carregar e explorar dados
def analise_exploratoria(caminho_arquivo):
    """
    Função básica para análise exploratória de dados
    """
    # Carregar dados
    df = pd.read_csv(caminho_arquivo)
    
    print("=" * 50)
    print("ANÁLISE EXPLORATÓRIA BÁSICA")
    print("=" * 50)
    
    # Informações gerais
    print(f"Shape do dataset: {df.shape}")
    print(f"\nPrimeiras 5 linhas:")
    print(df.head())
    
    print(f"\nÚltimas 5 linhas:")
    print(df.tail())
    
    print(f"\nTipos de dados:")
    print(df.dtypes)
    
    print(f"\nEstatísticas descritivas:")
    print(df.describe())
    
    print(f"\nValores nulos:")
    print(df.isnull().sum())
    
    return df

# Usar a função (substitua pelo caminho do seu arquivo)
# df = analise_exploratoria('seu_arquivo.csv')

bash

pip; install; pandas; matplotlib; seaborn; numpy;

