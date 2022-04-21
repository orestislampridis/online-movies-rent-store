import os

pg_user = os.environ.get('POSTGRES_USER')
pg_pass = os.environ.get('POSTGRES_PASSWORD')
pg_dbname = os.environ.get('POSTGRES_DB')
pg_host = 'db'
pg_port = 5432

SECRET_KEY = 'sUp3r_s3cr3t_k3y!'
DEV_DB = 'postgresql://postgres:1234@db:5432/flask_db'
PROD_DB = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_dbname}'
