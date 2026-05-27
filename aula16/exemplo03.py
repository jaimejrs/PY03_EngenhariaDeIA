# ============================================================
# REGRESSÃO LINEAR MÚLTIPLA
# Exemplo 03:
# Prever o valor total da nota fiscal usando:
# - quantidade total de itens
# - quantidade de produtos distintos
# - forma de pagamento
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
# Cada linha representa uma nota fiscal.
#
# Y  = valor_total_nota
# X1 = quantidade_total_itens
# X2 = quantidade_produtos_distintos
# X3 = forma_pagamento

sql = """
SELECT 
    nf.id AS id_nota_fiscal,
    fp.descricao AS forma_pagamento,
    SUM(inf.quantidade) AS quantidade_total_itens,
    COUNT(DISTINCT inf.id_produto) AS quantidade_produtos_distintos,
    SUM(inf.quantidade * inf.valor_unitario) AS valor_total_nota
FROM vendas.nota_fiscal nf
JOIN vendas.item_nota_fiscal inf 
    ON inf.id_nota_fiscal = nf.id
JOIN vendas.forma_pagamento fp 
    ON fp.id = nf.id_forma_pagto
GROUP BY 
    nf.id,
    fp.descricao
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
print(df[[
    "quantidade_total_itens",
    "quantidade_produtos_distintos",
    "valor_total_nota"
]].describe())

print("\nFormas de pagamento encontradas:")
print(df["forma_pagamento"].value_counts())


# ------------------------------------------------------------
# 4. TRATAMENTO BÁSICO DOS DADOS
# ------------------------------------------------------------

df = df.dropna(subset=[
    "forma_pagamento",
    "quantidade_total_itens",
    "quantidade_produtos_distintos",
    "valor_total_nota"
])

df = df[
    (df["quantidade_total_itens"] > 0) &
    (df["quantidade_produtos_distintos"] > 0) &
    (df["valor_total_nota"] > 0)
]

print("\nQuantidade de registros após tratamento:")
print(len(df))


# ------------------------------------------------------------
# 5. DEFININDO X E Y
# ------------------------------------------------------------

X = df[[
    "quantidade_total_itens",
    "quantidade_produtos_distintos",
    "forma_pagamento"
]]

y = df["valor_total_nota"]


# ------------------------------------------------------------
# 6. IDENTIFICANDO VARIÁVEIS NUMÉRICAS E CATEGÓRICAS
# ------------------------------------------------------------

variaveis_numericas = [
    "quantidade_total_itens",
    "quantidade_produtos_distintos"
]

variaveis_categoricas = [
    "forma_pagamento"
]


# ------------------------------------------------------------
# 7. PRÉ-PROCESSAMENTO
# ------------------------------------------------------------
# OneHotEncoder transforma a forma de pagamento em colunas numéricas.
#
# Exemplo:
# forma_pagamento = Cartão
# forma_pagamento = Dinheiro
# forma_pagamento = Pix

pre_processador = ColumnTransformer(
    transformers=[
        (
            "categoricas",
            OneHotEncoder(handle_unknown="ignore"),
            variaveis_categoricas
        ),
        (
            "numericas",
            "passthrough",
            variaveis_numericas
        )
    ]
)

print("\nPré-processador criado:")
print(pre_processador)
# ------------------------------------------------------------
# 8. CRIANDO O PIPELINE DO MODELO
# ------------------------------------------------------------

modelo = Pipeline(
    steps=[
        ("pre_processador", pre_processador),
        ("regressao", LinearRegression())
    ]
)


# ------------------------------------------------------------
# 9. DIVISÃO EM TREINO E TESTE
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ------------------------------------------------------------
# 10. TREINANDO O MODELO
# ------------------------------------------------------------

modelo.fit(X_train, y_train)


# ------------------------------------------------------------
# 11. FAZENDO PREVISÕES
# ------------------------------------------------------------

y_pred = modelo.predict(X_test)

resultado = pd.DataFrame({
    "quantidade_total_itens": X_test["quantidade_total_itens"],
    "quantidade_produtos_distintos": X_test["quantidade_produtos_distintos"],
    "forma_pagamento": X_test["forma_pagamento"],
    "valor_real": y_test,
    "valor_previsto": y_pred
})

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
# Esta parte exibe o peso de cada variável no modelo.

regressao = modelo.named_steps["regressao"]
pre_processador_treinado = modelo.named_steps["pre_processador"]

nomes_variaveis_categoricas = (
    pre_processador_treinado
    .named_transformers_["categoricas"]
    .get_feature_names_out(variaveis_categoricas)
)

nomes_variaveis = list(nomes_variaveis_categoricas) + variaveis_numericas

coeficientes = pd.DataFrame({
    "variavel": nomes_variaveis,
    "coeficiente": regressao.coef_
})

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
    label="Notas fiscais"
)

plt.xlabel("Valor real da nota fiscal")
plt.ylabel("Valor previsto da nota fiscal")
plt.title("Regressão Linear Múltipla - Valor Real x Valor Previsto")
plt.legend()
plt.grid(True)

plt.savefig("grafico_regressao_exemplo03_real_vs_previsto.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em: grafico_regressao_exemplo03_real_vs_previsto.png")


# ------------------------------------------------------------
# 15. GRÁFICO: ERROS DO MODELO
# ------------------------------------------------------------

erros = y_test - y_pred

plt.figure(figsize=(10, 6))

plt.scatter(
    y_pred,
    erros,
    alpha=0.5,
    label="Erros"
)

plt.axhline(
    y=0,
    linestyle="--",
    label="Erro zero"
)

plt.xlabel("Valor previsto")
plt.ylabel("Erro")
plt.title("Análise dos Erros da Regressão")
plt.legend()
plt.grid(True)

plt.savefig("grafico_regressao_exemplo03_erros.png", dpi=300, bbox_inches="tight")
plt.close()

print("Gráfico salvo em: grafico_regressao_exemplo03_erros.png")


# ------------------------------------------------------------
# 16. SIMULAÇÃO DE PREVISÃO
# ------------------------------------------------------------
# Ajuste a forma de pagamento conforme os valores existentes
# na sua base.

print("\nFormas de pagamento disponíveis na base:")
print(df["forma_pagamento"].unique())

nova_nota = pd.DataFrame({
    "quantidade_total_itens": [10],
    "quantidade_produtos_distintos": [4],
    "forma_pagamento": ["Dinheiro"]
})

valor_estimado = modelo.predict(nova_nota)

print("\nSimulação:")
print("Dados da nova nota fiscal:")
print(nova_nota)

print(f"\nValor estimado da nota fiscal: R$ {valor_estimado[0]:.2f}")
