import os

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

INPUT_FILE = os.path.join(TEMP_DIR, "dados_brutos_vendas.csv")
OUTPUT_FILE = os.path.join(TEMP_DIR, "dados_limpos_vendas.csv")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OUTPUT_OBJECT = "processed-data/dados_limpos_vendas.csv"


def main() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    # 1) IDs obrigatorios: converte para numerico e remove registros invalidos.
    id_columns = ["id", "id_vendedor", "id_cliente", "id_forma_pagto"]
    for column in id_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=[col for col in id_columns if col in df.columns])

    # 2) Valor da nota fiscal: numerico e nao negativo.
    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["valor"] = df["valor"].apply(lambda x: x if pd.notnull(x) and x >= 0 else None)
        media_valor = df["valor"].mean()
        if pd.notnull(media_valor):
            df["valor"] = df["valor"].fillna(media_valor).round(2)

    # 3) Data da venda: padroniza para datetime e remove datas invalidas.
    if "data_venda" in df.columns:
        df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
        df = df[df["data_venda"].notna()]

    # 4) Numero da nota: preenche ausentes e padroniza como string.
    if "numero_nf" in df.columns:
        df["numero_nf"] = df["numero_nf"].astype("string").fillna("SEM_NF")
        df["numero_nf"] = df["numero_nf"].replace("<NA>", "SEM_NF")

    # 5) Remove duplicidades por id da nota (caso existam).
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"], keep="last")

    df.to_csv(OUTPUT_FILE, index=False)

    s3 = boto3.client("s3")
    s3.upload_file(OUTPUT_FILE, BUCKET_NAME, S3_OUTPUT_OBJECT)

    print("\nLog - Qualidade de dados de vendas concluida e arquivo limpo enviado para o Data Lake.\n")


if __name__ == "__main__":
    main()
