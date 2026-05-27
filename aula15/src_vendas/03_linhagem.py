import json
import os
import hashlib
from datetime import datetime

import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
OBJECT_NAME = "raw-data/dados_brutos_vendas.csv"
LOCAL_CSV = os.path.join(TEMP_DIR, "dados_brutos_vendas.csv")
LOCAL_LINHAGEM = os.path.join(TEMP_DIR, "linhagem_vendas.json")
S3_LINHAGEM_OBJECT = "linhagem/linhagem_inicial_vendas.json"


def calcula_hash(file_name: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_name, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)
    s3 = boto3.client("s3")

    # Garante que a linhagem seja calculada sobre o mesmo arquivo publicado no lake.
    s3.download_file(BUCKET_NAME, OBJECT_NAME, LOCAL_CSV)

    hash_origem = calcula_hash(LOCAL_CSV)

    # Carrega o dataset apenas para validar leitura e compatibilidade do arquivo.
    df = pd.read_csv(LOCAL_CSV)

    linhagem = {
        "timestamp": datetime.utcnow().isoformat(),
        "arquivo_origem": OBJECT_NAME,
        "hash_origem": hash_origem,
        "total_linhas": int(len(df)),
        "transformacoes_aplicadas": "Nenhuma - dados brutos de vendas carregados",
        "arquivo_destino": "processed-data/dados_brutos_vendas.csv",
    }

    with open(LOCAL_LINHAGEM, "w", encoding="utf-8") as file:
        json.dump(linhagem, file, indent=4, ensure_ascii=False)

    s3.upload_file(LOCAL_LINHAGEM, BUCKET_NAME, S3_LINHAGEM_OBJECT)
    print("\nLog - Arquivo inicial de linhagem de vendas enviado para o Data Lake.\n")


if __name__ == "__main__":
    main()
