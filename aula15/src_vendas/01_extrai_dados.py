import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
try:
    import psycopg2
except ImportError as exc:
    raise SystemExit(
        "Dependencia ausente: instale 'psycopg2-binary' para conectar no PostgreSQL."
    ) from exc


HOST = os.getenv("DB_HOST")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = os.getenv("DB_PORT", 5432)

QUERY = """
SELECT
    id,
    id_vendedor,
    id_cliente,
    id_forma_pagto,
    data_venda,
    numero_nf,
    valor
FROM vendas.nota_fiscal
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dados_brutos_vendas.csv")


def extrair_dados() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = None
    try:
        conn = psycopg2.connect(
            host=HOST,
            dbname=DATABASE,
            user=USER,
            password=PASSWORD,
            port=PORT,
            connect_timeout=15,
        )
        df = pd.read_sql_query(QUERY, conn)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nDados extraidos com sucesso. Total de linhas: {len(df)}")
        print(f"Arquivo salvo em: {OUTPUT_FILE}\n")
    except Exception as exc:
        print(f"\nFalha na extracao: {exc}\n", file=sys.stderr)
        raise
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    extrair_dados()
