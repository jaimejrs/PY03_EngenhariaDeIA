import pandas as pd
import psycopg2

host = 'projeto.147229990245.us-east-1.redshift-serverless.amazonaws.com'
port = 5439
dbname = 'dev'
user = 'admin'
password = 'Jota119*'

query = """
SELECT
    *
FROM
    "vendas"."public"."stage_vendas_outras";
"""

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        sslmode='require'
    )

    df = pd.read_sql_query(query, conn)
    print(df)

except Exception as e:
    print("Erro ao consultar dados no Redshift:", e)

finally:
    if 'conn' in locals() and conn:
        conn.close()