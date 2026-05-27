import os

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

INPUT_FILE = os.path.join(TEMP_DIR, "dados_limpos_vendas.csv")
OUTPUT_FILE = os.path.join(TEMP_DIR, "dados_enriquecidos_vendas.csv")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OUTPUT_OBJECT = "enriched-data/dados_enriquecidos_vendas.csv"


def faixa_valor(valor: float) -> str:
    if pd.isnull(valor) or valor < 0:
        return "Desconhecido"
    if valor < 100:
        return "Baixo"
    if valor < 500:
        return "Medio"
    return "Alto"


def main() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["faixa_valor"] = df["valor"].apply(faixa_valor)

    if "data_venda" in df.columns:
        data = pd.to_datetime(df["data_venda"], errors="coerce")
        df["dia_semana"] = data.dt.day_name()
        df["fim_de_semana"] = data.dt.dayofweek.isin([5, 6])
        df["mes_venda"] = data.dt.month

    df.to_csv(OUTPUT_FILE, index=False)

    s3 = boto3.client("s3")
    s3.upload_file(OUTPUT_FILE, BUCKET_NAME, S3_OUTPUT_OBJECT)

    print("\nLog - Enriquecimento de vendas concluido e dados enviados para o Data Lake.\n")


if __name__ == "__main__":
    main()
