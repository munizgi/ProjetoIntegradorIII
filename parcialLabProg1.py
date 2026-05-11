import pandas as pd
import numpy as np
from scipy import stats
from sqlalchemy import create_engine

# conexão
engine = create_engine("postgresql+psycopg2://postgres:0401@localhost:5432/etl_teste")

# leitura do DW
query = """
SELECT
    quantidade,
    valor_total
FROM fato_movimentacao
WHERE quantidade > 0
AND valor_total > 0
"""

df = pd.read_sql(query, engine)

# variável contínua
df["valor_unitario"] = df["valor_total"] / df["quantidade"]

# população
pop = df["valor_unitario"]

# tamanho da população
N = len(pop)

# parâmetros estatísticos
z = 1.96          # 95%
sigma = pop.std()
E = 1             # margem de erro (ajustável)

# tamanho amostral inicial
n0 = ((z * sigma) / E) ** 2

# correção para população finita
n = (N * n0) / (N + n0 - 1)
n = int(np.ceil(n))

# amostra aleatória
amostra = pop.sample(n=n, random_state=42)

# estatísticas da amostra
media = amostra.mean()
desvio = amostra.std(ddof=1)

# intervalo de confiança
ic = stats.t.interval(
    confidence=0.95,
    df=len(amostra) - 1,
    loc=media,
    scale=stats.sem(amostra)
)

# teste de hipótese
hipotese = 90

t_stat, p_valor = stats.ttest_1samp(amostra, popmean=hipotese)

# saída
print(f"Tamanho da população: {N}")
print(f"Tamanho da amostra: {n}")
print(f"Média amostral: {media:.2f}")
print(f"Intervalo de confiança 95%: ({ic[0]:.2f}, {ic[1]:.2f})")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-valor: {p_valor:.4f}")
print(df["valor_unitario"].describe())


# A amostra ficou igual ao tamanho da população.
# Isso significa que o cálculo amostral concluiu que precisava praticamente de tudo.
# Com população pequena e dispersão relativamente alta, isso acontece.
# Acabamos analisando praticamente o conjunto inteiro.