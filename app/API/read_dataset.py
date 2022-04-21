import ast

import pandas as pd
from pandas import Series


def read_dataset(path_prefix):
    """
        Parse appropriate CSV file
        Parameters
        ----------
        path_prefix : String. Prefix to the data file

        Returns
        -------
        movie_df:
        movie_genre_df:
        genre_df:
    """
    # Load data into a pandas DataFrame
    movie_df = pd.read_csv(path_prefix)

    # Drop unneeded columns and rows with null values
    movie_df.drop(
        ['id', 'homepage', 'spoken_languages', 'production_companies', 'production_countries', 'status', 'tagline',
         'keywords'],
        axis=1, inplace=True)
    movie_df.dropna(inplace=True)

    # Drop rows with mistake budget/revenue entries
    movie_df.drop(movie_df.query('revenue == 0 or budget == 0').index, inplace=True)

    # Set pandas df index to 'movie_id'
    movie_df = movie_df.reset_index(drop=True)
    movie_df.index.name = 'movie_id'

    # Splitting the 'genres' column
    movie_df.loc[:, 'genres'] = movie_df['genres'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)])
    movie_df['genres'] = [','.join(map(str, genre)) for genre in movie_df['genres']]
    temp_df = movie_df.copy()

    s = temp_df['genres'].str.split(',').apply(Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = 'genres'
    del temp_df['genres']
    dt = temp_df.join(s)
    dt = dt[['genres']]
    dt['genre_id'] = dt.groupby(['genres']).ngroup()

    movie_genre_df = dt[['genre_id']]
    genre_df = dt.drop_duplicates().set_index('genre_id').sort_index()
    genre_df.rename(columns={'genres': 'genre'}, inplace=True)

    return movie_df, movie_genre_df, genre_df
