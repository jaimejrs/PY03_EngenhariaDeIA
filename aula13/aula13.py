import psycopg2

# Dados de conexão fornecidos
host = 'projeto.147229990245.us-east-1.redshift-serverless.amazonaws.com'
port = 5439
dbname = 'dev'
user = 'admin'
password = 'Jota119*'   # Substitua pela senha correta

# Conectando
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        sslmode='require'
    )
    print("✅ Conexão com Redshift Serverless estabelecida com sucesso!")

    # Testando uma consulta simples
    cursor = conn.cursor()
    cursor.execute("SELECT current_date;")
    result = cursor.fetchone()
    print("📅 Data atual do servidor:", result[0])

    # Fechando conexão
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Erro na conexão com Redshift:", e)