# ============================================================
# REGRESSÃO LINEAR SIMPLES
# Exemplo 01:
# Prever o valor total da nota fiscal com base na quantidade
# total de itens vendidos
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
# Aqui estamos criando uma base analítica por nota fiscal.
# Cada linha representa uma nota fiscal.
# A variável X será a quantidade total de itens.
# A variável Y será o valor total da nota.

sql = """
SELECT 
    nf.id AS id_nota_fiscal,
    SUM(inf.quantidade) AS quantidade_total_itens,
    SUM(inf.quantidade * inf.valor_unitario) AS valor_total_nota
FROM vendas.nota_fiscal nf
JOIN vendas.item_nota_fiscal inf 
    ON inf.id_nota_fiscal = nf.id
GROUP BY nf.id
ORDER BY nf.id;
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
print(df.describe())


# ------------------------------------------------------------
# 4. TRATAMENTO BÁSICO DOS DADOS
# ------------------------------------------------------------

df = df.dropna()

df = df[
    (df["quantidade_total_itens"] > 0) &
    (df["valor_total_nota"] > 0)
]

print("\nQuantidade de registros após tratamento:")
print(len(df))


# ------------------------------------------------------------
# 5. DEFININDO X E Y
# ------------------------------------------------------------
# X precisa estar em formato de matriz, por isso usamos dois colchetes.
# Y é a variável que queremos prever.

X = df[["quantidade_total_itens"]]
y = df["valor_total_nota"]


# ------------------------------------------------------------
# 6. DIVISÃO EM TREINO E TESTE
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ------------------------------------------------------------
# 7. TREINANDO O MODELO
# ------------------------------------------------------------

modelo = LinearRegression()
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
print(f"valor_total_nota = {intercepto:.2f} + {coeficiente:.2f} * quantidade_total_itens")


# ------------------------------------------------------------
# 9. FAZENDO PREVISÕES
# ------------------------------------------------------------

y_pred = modelo.predict(X_test)

resultado = pd.DataFrame({
    "quantidade_total_itens": X_test["quantidade_total_itens"],
    "valor_real": y_test,
    "valor_previsto": y_pred
})

print("\nComparação entre valor real e valor previsto:")
print(resultado.head())


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
plt.xlabel("Quantidade total de itens")
plt.ylabel("Valor total da nota fiscal")
plt.legend()
plt.grid(True)

arquivo_grafico = "grafico_regressao_exemplo01.png"
plt.savefig(arquivo_grafico, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nGráfico salvo em: {arquivo_grafico}")


# ------------------------------------------------------------
# 12. SIMULAÇÃO DE PREVISÃO
# ------------------------------------------------------------
# Exemplo: prever o valor de uma nota com 10 itens vendidos.

nova_quantidade = pd.DataFrame({
    "quantidade_total_itens": [10]
})

valor_estimado = modelo.predict(nova_quantidade)

print("\nSimulação:")
print(f"Para uma nota com 10 itens, o valor estimado é R$ {valor_estimado[0]:.2f}")

