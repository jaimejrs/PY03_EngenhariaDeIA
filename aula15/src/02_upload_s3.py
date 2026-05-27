# Imports
import boto3
from botocore.exceptions import ClientError

# Cria o client
s3 = boto3.client('s3')
region = 'us-east-1'  

# Variáveis
bucket_name = 'data-lake-bucket-147229990245'
file_name = 'temp/dados_brutos.csv'
object_name = 'raw-data/dados_brutos.csv'

# Função para verificar se o bucket existe
def verifica_cria_bucket(bucket_name):
    try:
        # Tenta acessar o bucket
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' já existe.")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            # Se o bucket não existir, ele será criado com a região especificada
            print(f"Bucket '{bucket_name}' não encontrado. Criando...")
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
            print(f"Bucket '{bucket_name}' criado com sucesso.")
        else:
            # Levanta o erro se não for um erro 404
            raise

# Verifica ou cria o bucket
verifica_cria_bucket(bucket_name)

# Upload do arquivo
s3.upload_file(file_name, bucket_name, object_name)

print(f"\nLog - Arquivo '{file_name}' enviado para '{bucket_name}/{object_name}' com sucesso.\n")


