from pathlib import Path

print("Script:", Path(__file__).resolve())
print("Pasta:", Path(__file__).resolve().parent)
print("CSV existe?", (Path(__file__).resolve().parent / "24p26.csv").exists())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sklearn.linear_model import LinearRegression

# puxando o arquivo

dados = pd.read_csv(
    '24p26.csv',
    sep=';'
)

# ajustando a data

dados['data'] = pd.to_datetime(dados['data'])

# =agrupamento por dia

dados_diarios = (
    dados.groupby('data')['preco_venda']
    .mean()
    .reset_index()
)

# retirando os outliers

Q1 = dados_diarios['preco_venda'].quantile(0.25)

Q3 = dados_diarios['preco_venda'].quantile(0.75)

IQR = Q3 - Q1

limite_inferior = Q1 - 1.5 * IQR

limite_superior = Q3 + 1.5 * IQR

dados_limpos = dados_diarios[
    (dados_diarios['preco_venda'] >= limite_inferior) &
    (dados_diarios['preco_venda'] <= limite_superior)
].copy()

# agrupamento semanal

dados_semanais = (
    dados_limpos
    .set_index('data')
    .resample('W')['preco_venda']
    .mean()
    .reset_index()
)

# ajustando as variaveis de tempo

dados_semanais['semanas'] = np.arange(len(dados_semanais))

x = dados_semanais[['semanas']]

y = dados_semanais['preco_venda']

# treinando o modelo

modelo = LinearRegression()

modelo.fit(x, y)

# previsão 8 semanas

futuras_semanas = np.arange(
    len(dados_semanais),
    len(dados_semanais) + 8
).reshape(-1, 1)

previsoes = modelo.predict(futuras_semanas)

previsoes = np.round(previsoes, 2)

# datas futuras

ultima_data = dados_semanais['data'].max()

datas_futuras = pd.date_range(
    start=ultima_data + pd.Timedelta(weeks=1),
    periods=8,
    freq='W'
)

# resultado

resultado_previsao = pd.DataFrame({

    'Semana': datas_futuras,

    'Preço Previsto': previsoes

})

print('\n========== PREVISÃO SEMANAL ==========')

print(resultado_previsao)

# gráfico

plt.figure(figsize=(16,8))

# histórico

plt.plot(
    dados_semanais['data'],
    dados_semanais['preco_venda'],
    linewidth=3,
    label='Histórico Semanal'
)

# previsão

plt.plot(
    datas_futuras,
    previsoes,
    '--',
    linewidth=3,
    label='Previsão média Próximas 8 Semanas'
)

# sombreado

plt.fill_between(
    datas_futuras,
    previsoes,
    alpha=0.2
)

# formatação das datas

ax = plt.gca()

ax.xaxis.set_major_formatter(
    mdates.DateFormatter('%d/%m/%Y')
)

# títulos

plt.title(
    'Previsão Semanal Média Sem Outliers',
    fontsize=18
)

plt.xlabel(
    'Semana',
    fontsize=12
)

plt.ylabel(
    'Preço Médio',
    fontsize=12
)

plt.legend()

plt.grid(True)

plt.xticks(rotation=30)

plt.tight_layout()

plt.show()