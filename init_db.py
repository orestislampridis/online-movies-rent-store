import ast

import pandas as pd
from pandas import Series
from sqlalchemy import create_engine

# Connect to database
engine = create_engine('postgresql://postgres:1234@localhost:5432/flask_db')

# Load data into a pandas DataFrame
df = pd.read_csv('dataset/tmdb_5000_movies.csv')

# Drop unneeded columns and rows with null values
df.drop(
    ['id', 'homepage', 'spoken_languages', 'production_companies', 'production_countries', 'status', 'tagline',
     'keywords'],
    axis=1, inplace=True)
df.dropna(inplace=True)

# Drop rows with mistake budget/revenue entries
df.drop(df.query('revenue == 0 or budget == 0').index, inplace=True)

# Set pandas df index to 'movie_id'
df = df.reset_index(drop=True)
df.index.name = 'movie_id'

# Splitting the 'genres' column
df.loc[:, 'genres'] = df['genres'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)])
df['genres'] = [','.join(map(str, l)) for l in df['genres']]
temp_df = df.copy()

s = temp_df['genres'].str.split(',').apply(Series, 1).stack()
s.index = s.index.droplevel(-1)
s.name = 'genres'
del temp_df['genres']
dt = temp_df.join(s)
dt = dt[['genres']]
dt['genre_id'] = dt.groupby(['genres']).ngroup()

movie_genre_df = dt[['genre_id']]
genre_df = dt.drop_duplicates().set_index('genre_id').sort_index()

# Open a cursor to perform database operations
conn = engine.raw_connection()
cur = conn.cursor()

# Create table for movies
cur.execute('DROP TABLE IF EXISTS movie cascade;')
conn.commit()

df.to_sql(name='movie', con=engine, index_label='movie_id')
with engine.connect() as con:
    con.execute('ALTER TABLE movie ADD PRIMARY KEY (movie_id);')

movie_genre_df.to_sql(name='movie_genre', con=engine, index='movie_id', if_exists='replace')
with engine.connect() as con:
    con.execute('ALTER TABLE movie_genre ADD PRIMARY KEY (movie_id, genre_id);')

genre_df.to_sql(name='genre', con=engine, index_label='genre_id', if_exists='replace')
with engine.connect() as con:
    con.execute('ALTER TABLE genre ADD PRIMARY KEY (genre_id);')

cur.execute('DROP TABLE IF EXISTS "user";')
cur.execute('CREATE TABLE "user" (user_id serial PRIMARY KEY,'
            'email varchar (50) NOT NULL,'
            'password text NOT NULL,'
            'first_name varchar (50) NOT NULL,'
            'last_name varchar (50) NOT NULL);'
            )

cur.execute('DROP TABLE IF EXISTS rental cascade;')
cur.execute('CREATE TABLE rental (rental_id serial PRIMARY KEY,'
            'movie_id serial references movie(movie_id) NOT NULL,'
            'user_id serial references "user"(user_id) NOT NULL,'
            'date_start timestamptz NOT NULL);'
            )

conn.commit()

cur.close()
conn.close()
