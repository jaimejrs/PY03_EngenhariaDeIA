# ============================================================
# REGRESSÃO LINEAR MÚLTIPLA
# Exemplo 04:
# Prever o valor de venda real usando:
# - valor de custo
# - valor de venda cadastrado
# - quantidade vendida
# - categoria do produto
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline


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
# Cada linha representa um item vendido.
#
# Y  = valor_venda_real
# X1 = valor_custo
# X2 = valor_venda_cadastrado
# X3 = quantidade
# X4 = categoria

sql = """
SELECT 
    inf.id AS id_item,
    p.id AS id_produto,
    p.nome AS produto,
    c.descricao AS categoria,
    p.valor_custo,
    p.valor_venda AS valor_venda_cadastrado,
    inf.quantidade,
    inf.valor_venda_real
FROM vendas.item_nota_fiscal inf
JOIN vendas.produto p 
    ON p.id = inf.id_produto
JOIN vendas.categoria c 
    ON c.id = p.id_categoria
WHERE p.valor_custo IS NOT NULL
  AND p.valor_venda IS NOT NULL
  AND inf.valor_venda_real IS NOT NULL
  AND inf.quantidade IS NOT NULL
  AND p.valor_custo > 0
  AND p.valor_venda > 0
  AND inf.valor_venda_real > 0
  AND inf.quantidade > 0
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
print(
    df[
        [
            "valor_custo",
            "valor_venda_cadastrado",
            "quantidade",
            "valor_venda_real",
        ]
    ].describe()
)

print("\nCategorias encontradas:")
print(df["categoria"].value_counts())


# ------------------------------------------------------------
# 4. TRATAMENTO BÁSICO DOS DADOS
# ------------------------------------------------------------

df = df.dropna(
    subset=[
        "categoria",
        "valor_custo",
        "valor_venda_cadastrado",
        "quantidade",
        "valor_venda_real",
    ]
)

df = df[
    (df["valor_custo"] > 0)
    & (df["valor_venda_cadastrado"] > 0)
    & (df["quantidade"] > 0)
    & (df["valor_venda_real"] > 0)
]

print("\nQuantidade de registros após tratamento:")
print(len(df))


# ------------------------------------------------------------
# 5. DEFININDO X E Y
# ------------------------------------------------------------

X = df[
    [
        "valor_custo",
        "valor_venda_cadastrado",
        "quantidade",
        "categoria",
    ]
]

y = df["valor_venda_real"]


# ------------------------------------------------------------
# 6. VARIÁVEIS NUMÉRICAS E CATEGÓRICAS
# ------------------------------------------------------------

variaveis_numericas = [
    "valor_custo",
    "valor_venda_cadastrado",
    "quantidade",
]

variaveis_categoricas = [
    "categoria",
]


# ------------------------------------------------------------
# 7. PRÉ-PROCESSAMENTO
# ------------------------------------------------------------
# A categoria é texto.
# Por isso, usamos OneHotEncoder para transformar em colunas numéricas.

pre_processador = ColumnTransformer(
    transformers=[
        (
            "categoricas",
            OneHotEncoder(handle_unknown="ignore"),
            variaveis_categoricas,
        ),
        (
            "numericas",
            "passthrough",
            variaveis_numericas,
        ),
    ]
)


# ------------------------------------------------------------
# 8. CRIANDO O PIPELINE
# ------------------------------------------------------------

modelo = Pipeline(
    steps=[
        ("pre_processador", pre_processador),
        ("regressao", LinearRegression()),
    ]
)


# ------------------------------------------------------------
# 9. DIVISÃO EM TREINO E TESTE
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)


# ------------------------------------------------------------
# 10. TREINANDO O MODELO
# ------------------------------------------------------------

modelo.fit(X_train, y_train)


# ------------------------------------------------------------
# 11. FAZENDO PREVISÕES
# ------------------------------------------------------------

y_pred = modelo.predict(X_test)

resultado = pd.DataFrame(
    {
        "valor_custo": X_test["valor_custo"],
        "valor_venda_cadastrado": X_test["valor_venda_cadastrado"],
        "quantidade": X_test["quantidade"],
        "categoria": X_test["categoria"],
        "valor_real": y_test,
        "valor_previsto": y_pred,
    }
)

print("\nComparação entre valor real e valor previsto:")
print(resultado.head(10))


# ------------------------------------------------------------
# 12. AVALIAÇÃO DO MODELO
# ------------------------------------------------------------

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nMétricas de avaliação:")
print(f"MAE  - Erro médio absoluto: {mae:.2f}")
print(f"MSE  - Erro quadrático médio: {mse:.2f}")
print(f"R²   - Coeficiente de determinação: {r2:.4f}")


# ------------------------------------------------------------
# 13. COEFICIENTES DO MODELO
# ------------------------------------------------------------

regressao = modelo.named_steps["regressao"]
pre_processador_treinado = modelo.named_steps["pre_processador"]

nomes_variaveis_categoricas = (
    pre_processador_treinado
    .named_transformers_["categoricas"]
    .get_feature_names_out(variaveis_categoricas)
)

nomes_variaveis = list(nomes_variaveis_categoricas) + variaveis_numericas

coeficientes = pd.DataFrame(
    {
        "variavel": nomes_variaveis,
        "coeficiente": regressao.coef_,
    }
)

print("\nIntercepto do modelo:")
print(f"{regressao.intercept_:.2f}")

print("\nCoeficientes do modelo:")
print(coeficientes.sort_values(by="coeficiente", ascending=False))


# ------------------------------------------------------------
# 14. GRÁFICO: VALOR REAL X VALOR PREVISTO
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.scatter(
    y_test,
    y_pred,
    alpha=0.5,
    label="Itens vendidos",
)

plt.xlabel("Valor real de venda")
plt.ylabel("Valor previsto de venda")
plt.title("Regressão Linear Múltipla - Valor Real x Valor Previsto")
plt.legend()
plt.grid(True)

plt.savefig(
    "grafico_regressao_exemplo04_real_vs_previsto.png",
    dpi=300,
    bbox_inches="tight",
)

plt.show()

print("\nGráfico salvo em: grafico_regressao_exemplo04_real_vs_previsto.png")


# ------------------------------------------------------------
# 15. GRÁFICO: ERROS DO MODELO
# ------------------------------------------------------------

erros = y_test - y_pred

plt.figure(figsize=(10, 6))

plt.scatter(
    y_pred,
    erros,
    alpha=0.5,
    label="Erros",
)

plt.axhline(
    y=0,
    linestyle="--",
    label="Erro zero",
)

plt.xlabel("Valor previsto")
plt.ylabel("Erro")
plt.title("Análise dos Erros da Regressão")
plt.legend()
plt.grid(True)

plt.savefig(
    "grafico_regressao_exemplo04_erros.png",
    dpi=300,
    bbox_inches="tight",
)

plt.show()

print("Gráfico salvo em: grafico_regressao_exemplo04_erros.png")


# ------------------------------------------------------------
# 16. SIMULAÇÃO DE PREVISÃO
# ------------------------------------------------------------

print("\nCategorias disponíveis na base:")
print(df["categoria"].unique())


# IMPORTANTE:
# Troque a categoria abaixo por uma categoria que exista na sua base.
novo_item = pd.DataFrame(
    {
        "valor_custo": [100],
        "valor_venda_cadastrado": [250],
        "quantidade": [2],
        "categoria": ["Móveis"],
    }
)

valor_estimado = modelo.predict(novo_item)

print("\nSimulação:")
print("Dados do novo item:")
print(novo_item)

print(f"\nValor de venda real estimado: R$ {valor_estimado[0]:.2f}")