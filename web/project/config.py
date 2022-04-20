DEV_DB = 'postgresql://postgres:1234@localhost:5432/flask_db'

pg_user = 'postgres'
pg_pass = 'admin'
pg_dbname = 'flask_db'
pg_host = 'localhost'
pg_port = 5432

PROD_DB = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_dbname}'
