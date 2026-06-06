import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Puxando a base
dados = pd.read_csv('24p26.csv')

# Ajuste de data

dados['data'] = pd.to_datetime(
    dados['data'],
    dayfirst=True
)

# Agrupamento da data

dados_diarios = (
    dados.groupby('data')['preco_venda']
    .mean()
    .reset_index()
)

# Valores estatísticos

media_preco = dados_diarios['preco_venda'].mean()

mediana_preco = dados_diarios['preco_venda'].median()

desvio_padrao = dados_diarios['preco_venda'].std()

print('\n========== ESTATÍSTICAS ==========')

print(f'Ticket Médio: {media_preco:.2f}')

print(f'Mediana: {mediana_preco:.2f}')

print(f'Desvio Padrão: {desvio_padrao:.2f}')

# encontrando os outliers (mede o intervalo interquartil)

Q1 = dados_diarios['preco_venda'].quantile(0.25)

Q3 = dados_diarios['preco_venda'].quantile(0.75)

IQR = Q3 - Q1

limite_inferior = Q1 - 1.5 * IQR

limite_superior = Q3 + 1.5 * IQR

# identificando os outliers para o filtro

outliers = dados_diarios[
    (dados_diarios['preco_venda'] < limite_inferior) |
    (dados_diarios['preco_venda'] > limite_superior)
]
outliers['preco_venda'] = outliers['preco_venda'].round(2)
print('\n========== OUTLIERS IDENTIFICADOS ==========')

print(outliers)

# remoção dos outliers

dados_sem_outliers = dados_diarios[
    (dados_diarios['preco_venda'] >= limite_inferior) &
    (dados_diarios['preco_venda'] <= limite_superior)
]

dados_sem_outliers['preco_venda'] = (
    dados_sem_outliers['preco_venda'].round(2)
)

print('\n========== DADOS SEM OUTLIERS ==========')

print(dados_sem_outliers.head())

# gráfico

plt.figure(figsize=(14,7))

# dados originais

plt.plot(
    dados_diarios['data'],
    dados_diarios['preco_venda'],
    label='Dados Originais',
    linewidth=2
)

# dados sem os outliers

plt.plot(
    dados_sem_outliers['data'],
    dados_sem_outliers['preco_venda'],
    label='Dados Sem Outliers',
    linewidth=2
)


# média

plt.axhline(
    media_preco,
    linestyle='--',
    label=f'Média: {media_preco:.2f}'
)

# mediana

plt.axhline(
    mediana_preco,
    linestyle=':',
    label=f'Mediana: {mediana_preco:.2f}'
)

plt.title('Análise Estatística dos Dados')

plt.xlabel('Data')

plt.ylabel('Preço Médio')

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()