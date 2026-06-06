import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

# =====================================================
# 1 - IMPORTAÇÃO DOS DADOS
# =====================================================

df = pd.read_csv(
    "24p26.csv",   # ALTERAR SE NECESSÁRIO
    sep=";",
    decimal=","
)

print("\nCOLUNAS ENCONTRADAS:")
print(df.columns)

# =====================================================
# 2 - SELEÇÃO DAS VARIÁVEIS
# =====================================================

X = df[["qtde_prod"]]

y = df["preco_venda"]

# =====================================================
# 3 - AJUSTE DO MODELO
# =====================================================

modelo = LinearRegression()

modelo.fit(X, y)

# =====================================================
# 4 - PREVISÕES
# =====================================================

previsoes = modelo.predict(X)

# =====================================================
# 5 - COEFICIENTES
# =====================================================

intercepto = modelo.intercept_
coeficiente = modelo.coef_[0]

print("\n==============================")
print("MODELO DE REGRESSÃO LINEAR")
print("==============================")

print(f"\nIntercepto (β0): {intercepto:.4f}")
print(f"Coeficiente (β1): {coeficiente:.4f}")

print(
    f"\nEquação:"
    f"\nPreco_Venda = {intercepto:.4f} + ({coeficiente:.4f} * Quantidade)"
)

# =====================================================
# 6 - MÉTRICAS DO MODELO
# =====================================================

r2 = r2_score(y, previsoes)

mae = mean_absolute_error(y, previsoes)

rmse = np.sqrt(
    mean_squared_error(y, previsoes)
)

print("\n==============================")
print("AVALIAÇÃO DO MODELO")
print("==============================")

print(f"\nR²: {r2:.4f}")

print(f"MAE: {mae:.4f}")

print(f"RMSE: {rmse:.4f}")

# =====================================================
# 7 - TABELA DE RESULTADOS
# =====================================================

resultado = pd.DataFrame({
    "Quantidade": X["qtde_prod"],
    "Preco_Real": y,
    "Preco_Previsto": previsoes
})

print("\nPRIMEIRAS LINHAS:")
print(resultado.head())

resultado.to_csv(
    "resultado_regressao.csv",
    index=False,
    sep=";"
)

# =====================================================
# 8 - GRÁFICO
# =====================================================

plt.figure(figsize=(10,6))

plt.scatter(
    X,
    y,
    alpha=0.4
)

plt.plot(
    X,
    previsoes
)

plt.title(
    "Regressão Linear - Quantidade x Preço de Venda"
)

plt.xlabel("Quantidade")

plt.ylabel("Preço de Venda")

plt.tight_layout()

plt.show()

print("\nArquivo gerado:")
print("resultado_regressao.csv")