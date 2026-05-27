# ============================================================
# REGRESSÃO LINEAR SIMPLES
# Exemplo 02:
# Prever o valor de venda real do item com base no valor
# de custo do produto
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ------------------------------------------------------------
# 1. CONEXÃO COM O BANCO DE DADOS POSTGRESQL
# ------------------------------------------------------------

usuario = "datadt_data_analytics"
senha = "DataAnalytics$100"
host = "postgresql-datadt.alwaysdata.net"
porta = "5432"
banco = "datadt_digital_corporativo"

engine = create_engine(
    f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"
)


# ------------------------------------------------------------
# 2. CONSULTA SQL
# ------------------------------------------------------------
# Cada linha representa um item vendido em uma nota fiscal.
# X = valor_custo do produto
# Y = valor_venda_real praticado na venda

sql = """
SELECT 
    inf.id AS id_item,
    p.id AS id_produto,
    p.nome AS produto,
    p.valor_custo,
    p.valor_venda AS valor_venda_cadastrado,
    inf.valor_unitario as valor_venda_real
FROM vendas.item_nota_fiscal inf
JOIN vendas.produto p 
    ON p.id = inf.id_produto
WHERE p.valor_custo IS NOT NULL
  AND inf.valor_unitario IS NOT NULL
  AND p.valor_custo > 0
  AND inf.valor_unitario > 0
ORDER BY inf.id;
"""


# ------------------------------------------------------------
# 3. CARREGANDO OS DADOS
# ------------------------------------------------------------

df = pd.read_sql(sql, engine)

print("Primeiras linhas da base:")
print(df.head())

print("\nInformações da base:")
print(df.info())

print("\nResumo estatístico:")
print(df[["valor_custo", "valor_venda_real"]].describe())


# ------------------------------------------------------------
# 4. TRATAMENTO BÁSICO DOS DADOS
# ------------------------------------------------------------

df = df.dropna(subset=["valor_custo", "valor_venda_real"])

df = df[
    (df["valor_custo"] > 0) &
    (df["valor_venda_real"] > 0)
]

print("\nQuantidade de registros após tratamento:")
print(len(df))


# ------------------------------------------------------------
# 5. DEFININDO X E Y
# ------------------------------------------------------------
# X precisa ser uma matriz, por isso usamos dois colchetes.
# Y é a variável que queremos prever.

X = df[["valor_custo"]]
y = df["valor_venda_real"]


# ------------------------------------------------------------
# 6. DIVISÃO EM TREINO E TESTE
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42
)


# ------------------------------------------------------------
# 7. TREINANDO O MODELO
# ------------------------------------------------------------
# modelo = LinearRegression()
modelo = LinearRegression(fit_intercept=False)
modelo.fit(X_train, y_train)


# ------------------------------------------------------------
# 8. COEFICIENTES DO MODELO
# ------------------------------------------------------------

intercepto = modelo.intercept_
coeficiente = modelo.coef_[0]

print("\nModelo treinado:")
print(f"Intercepto: {intercepto:.2f}")
print(f"Coeficiente: {coeficiente:.2f}")

print("\nEquação da regressão:")
print(f"valor_venda_real = {intercepto:.2f} + {coeficiente:.2f} * valor_custo")


# ------------------------------------------------------------
# 9. FAZENDO PREVISÕES
# ------------------------------------------------------------

y_pred = modelo.predict(X_test)

resultado = pd.DataFrame({
    "valor_custo": X_test["valor_custo"],
    "valor_real": y_test,
    "valor_previsto": y_pred
})

print("\nComparação entre valor real e valor previsto:")
print(resultado.head(10))


# ------------------------------------------------------------
# 10. AVALIAÇÃO DO MODELO
# ------------------------------------------------------------

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nMétricas de avaliação:")
print(f"MAE  - Erro médio absoluto: {mae:.2f}")
print(f"MSE  - Erro quadrático médio: {mse:.2f}")
print(f"R²   - Coeficiente de determinação: {r2:.4f}")


# ------------------------------------------------------------
# 11. VISUALIZAÇÃO DOS DADOS E DA RETA DE REGRESSÃO
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    X,
    y,
    label="Dados reais"
)

plt.plot(
    X,
    modelo.predict(X),
    label="Reta de regressão"
)

plt.title("Regressão Linear Simples")
plt.xlabel("Valor de custo do produto")
plt.ylabel("Valor de venda real")
plt.legend()
plt.grid(True)

arquivo_grafico = "grafico_regressao_exemplo02.png"
plt.savefig(arquivo_grafico, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nGráfico salvo em: {arquivo_grafico}")


# ------------------------------------------------------------
# 12. SIMULAÇÃO DE PREVISÃO
# ------------------------------------------------------------
# Exemplo: prever o valor de venda real de um produto
# cujo custo é R$ 100,00.

novo_custo = pd.DataFrame({
    "valor_custo": [100]
})

valor_estimado = modelo.predict(novo_custo)

print("\nSimulação:")
print(f"Para um produto com custo de R$ 100,00, o valor de venda estimado é R$ {valor_estimado[0]:.2f}")



