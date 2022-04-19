from app import db
from models import Movie, Genre, MovieGenre, User, Rental
from read_dataset import read_dataset

db.drop_all()

user = User()
movie = Movie()
rental = Rental()
genre = Genre()
movie_genre = MovieGenre()

db.create_all()

movie_df, movie_genre_df, genre_df = read_dataset(path_prefix='dataset/tmdb_5000_movies.csv')

movie_df.to_sql(name='movie', con=db.engine, index_label='movie_id', if_exists='append')
movie_genre_df.to_sql(name='movie_genre', con=db.engine, index='movie_id', if_exists='append')
genre_df.to_sql(name='genre', con=db.engine, index_label='genre_id', if_exists='append')

db.create_all()
