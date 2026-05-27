import json
import os

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

INPUT_FILE = os.path.join(TEMP_DIR, "dados_brutos_vendas.csv")
OUTPUT_FILE = os.path.join(TEMP_DIR, "observabilidade_vendas.json")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OUTPUT_OBJECT = "observabilidade/observabilidade_inicial_vendas.json"


def main() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    # Converte campos esperados como numericos para melhorar as metricas.
    numeric_columns = ["id", "id_vendedor", "id_cliente", "id_forma_pagto", "valor"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")

    variaveis_categoricas = df.select_dtypes(include=["object"]).columns
    variaveis_quantitativas = df.select_dtypes(include=["number"]).columns

    estatisticas_quantitativas = (
        df[variaveis_quantitativas]
        .describe()
        .map(lambda x: float(x) if pd.notnull(x) else None)
        .to_dict()
    )

    estatisticas_categoricas = {
        coluna: {
            "total": int(df[coluna].count()),
            "valores_unicos": int(df[coluna].nunique()),
            "valor_mais_frequente": (
                df[coluna].mode()[0] if not df[coluna].mode().empty else None
            ),
            "frequencia_do_valor_mais_frequente": (
                int(df[coluna].value_counts().iloc[0])
                if not df[coluna].value_counts().empty
                else None
            ),
        }
        for coluna in variaveis_categoricas
    }

    observabilidade = {
        "total_linhas": int(len(df)),
        "colunas": df.columns.tolist(),
        "colunas_nulas": df.isnull().sum().astype(int).to_dict(),
        "tipos_dados": df.dtypes.astype(str).to_dict(),
        "estatisticas_quantitativas": estatisticas_quantitativas,
        "estatisticas_categoricas": estatisticas_categoricas,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(observabilidade, file, indent=4, ensure_ascii=False)

    s3 = boto3.client("s3")
    s3.upload_file(OUTPUT_FILE, BUCKET_NAME, S3_OUTPUT_OBJECT)

    print("\nLog - Arquivo de observabilidade de vendas enviado para o Data Lake.\n")


if __name__ == "__main__":
    main()
