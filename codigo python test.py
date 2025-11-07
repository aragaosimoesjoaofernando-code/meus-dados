import csv
from collections import defaultdict

def ler_arquivos():
    # Ler arquivo de clientes
    clientes = {}
    try:
        with open('cliente.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Tenta encontrar a coluna do código do cliente
                codigo_key = None
                for key in row.keys():
                    if 'codigo' in key.lower() or 'id' in key.lower() or 'cliente' in key.lower():
                        codigo_key = key
                        break
                
                if codigo_key:
                    clientes[row[codigo_key]] = row
    except FileNotFoundError:
        print("Arquivo cliente.csv não encontrado")
        return None, None

    # Ler arquivo de vendas e contar por cliente
    vendas_por_cliente = defaultdict(int)
    try:
        with open('vendas.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Tenta encontrar a coluna do código do cliente
                codigo_key = None
                for key in row.keys():
                    if 'codigo' in key.lower() or 'id' in key.lower() or 'cliente' in key.lower():
                        codigo_key = key
                        break
                
                if codigo_key and row[codigo_key] in clientes:
                    vendas_por_cliente[row[codigo_key]] += 1
    except FileNotFoundError:
        print("Arquivo vendas.csv não encontrado")
        return None, None

    return clientes, vendas_por_cliente

def main():
    clientes, vendas_por_cliente = ler_arquivos()
    
    if not clientes or not vendas_por_cliente:
        print("Erro ao ler os arquivos.")
        return

    # Ordenar clientes por número de vendas
    clientes_ordenados = sorted(
        vendas_por_cliente.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if not clientes_ordenados:
        print("Nenhuma venda encontrada.")
        return

    # Mostrar o cliente com mais vendas
    codigo_mais_vendas, total_mais_vendas = clientes_ordenados[0]
    cliente_mais_vendas = clientes[codigo_mais_vendas]
    
    print("Cliente com mais vendas:")
    print(f"Código: {codigo_mais_vendas}")
    print(f"Nome: {cliente_mais_vendas.get('nome', 'N/A')}")
    print(f"Total de vendas: {total_mais_vendas}")

    # Pegar os dois clientes com mais vendas
    top_2_clientes = []
    for i in range(min(2, len(clientes_ordenados))):
        codigo, total_vendas = clientes_ordenados[i]
        cliente_info = clientes[codigo].copy()
        cliente_info['total_vendas'] = total_vendas
        cliente_info['codigo_cliente'] = codigo
        top_2_clientes.append(cliente_info)

    # Gerar novo arquivo CSV
    with open('top_2_clientes_vendas.csv', 'w', newline='', encoding='utf-8') as file:
        if top_2_clientes:
            fieldnames = ['codigo_cliente', 'nome', 'total_vendas']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for cliente in top_2_clientes:
                writer.writerow({
                    'codigo_cliente': cliente['codigo_cliente'],
                    'nome': cliente.get('nome', 'N/A'),
                    'total_vendas': cliente['total_vendas']
                })

    print(f"\nArquivo 'top_2_clientes_vendas.csv' gerado com sucesso!")
    print("\nTop 2 clientes com mais vendas:")
    for cliente in top_2_clientes:
        print(f"Código: {cliente['codigo_cliente']}, Nome: {cliente.get('nome', 'N/A')}, Vendas: {cliente['total_vendas']}")

if __name__ == "__main__":
    main()

# After running this script, push changes to the repository:
# git push origin main

import subprocess
subprocess.run(["git", "add", "top_2_clientes_vendas.csv"])
subprocess.run(["git", "commit", "-m", "Adiciona arquivo com os top 2 clientes com mais vendas"])
subprocess.run(["git", "push", "origin", "main"])   

