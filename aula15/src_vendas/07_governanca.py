import os

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

INPUT_FILE = os.path.join(TEMP_DIR, "dados_enriquecidos_vendas.csv")
OUTPUT_FILE = os.path.join(TEMP_DIR, "dados_governados_vendas.csv")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OUTPUT_OBJECT = "governed-data/dados_governados_vendas.csv"


def mascarar_id(valor) -> str:
    if pd.isnull(valor):
        return ""
    valor_str = str(valor)
    if len(valor_str) <= 2:
        return "*" * len(valor_str)
    return valor_str[:2] + "*" * (len(valor_str) - 2)


def mascarar_nf(valor) -> str:
    if pd.isnull(valor):
        return ""
    valor_str = str(valor)
    if len(valor_str) <= 3:
        return "*" * len(valor_str)
    return "*" * (len(valor_str) - 3) + valor_str[-3:]


def main() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    if "id_cliente" in df.columns:
        df["id_cliente_mascarado"] = df["id_cliente"].apply(mascarar_id)
        df = df.drop(columns=["id_cliente"])

    if "id_vendedor" in df.columns:
        df["id_vendedor_mascarado"] = df["id_vendedor"].apply(mascarar_id)
        df = df.drop(columns=["id_vendedor"])

    if "numero_nf" in df.columns:
        df["numero_nf_mascarado"] = df["numero_nf"].apply(mascarar_nf)
        df = df.drop(columns=["numero_nf"])

    df.to_csv(OUTPUT_FILE, index=False)

    s3 = boto3.client("s3")
    s3.upload_file(OUTPUT_FILE, BUCKET_NAME, S3_OUTPUT_OBJECT)

    print("\nLog - Governanca de dados de vendas concluida e arquivo enviado para o Data Lake.\n")


if __name__ == "__main__":
    main()
