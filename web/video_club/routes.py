from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import jsonify, request, make_response
from video_club import app, bcrypt, database
from video_club.database import commit_changes
from video_club.models import Movie, User, Genre, MovieGenre, Rental
from video_club import db

# decorator for verifying the JWT
from video_club.read_dataset import read_dataset


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            current_user = User.query \
                .filter_by(user_id=data['user_id']) \
                .first()
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged-in user
        return f(current_user, *args, **kwargs)

    return decorated


@app.before_first_request
def create_tables():
    db.create_all()

    # Check if the existing movie table contain data, if not then initialize
    if len(db.session().query(Movie).all()) == 0:
        movie_df, movie_genre_df, genre_df = read_dataset(path_prefix='video_club/dataset/tmdb_5000_movies.csv')

        movie_df.to_sql(name='movie', con=db.engine, index_label='movie_id', if_exists='append', chunksize=1000)
        movie_genre_df.to_sql(name='movie_genre', con=db.engine, index='movie_id', if_exists='append', chunksize=1000)
        genre_df.to_sql(name='genre', con=db.engine, index_label='genre_id', if_exists='append', chunksize=1000)


@app.route('/create_user', methods=['POST'])
def create_user():
    auth = request.form

    email = auth.get("email")
    password = bcrypt.generate_password_hash(auth.get("password")).decode('utf-8')
    first_name = auth.get("first_name")
    last_name = auth.get("last_name")

    database.add_instance(User, email=email, password=password, first_name=first_name, last_name=last_name)

    return make_response('User successfully created!', 201)


@app.route('/login', methods=['POST'])
def login():
    auth = request.form

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query.filter_by(email=auth.get("email")).first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if bcrypt.check_password_hash(user.password, request.form["password"]):
        token = jwt.encode({
            'user_id': user.user_id,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, app.secret_key)

        return make_response(jsonify({'token': token}), 201)

    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'})


@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = database.get_all(User)

    output = []
    for user in users:
        output.append({
            'user_id': user.user_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })

    return jsonify({'users': output})


@app.route('/get_all_movie_titles', methods=['GET'])
@token_required
def get_movies(current_user):
    movies = database.get_all(Movie)

    output = []
    for movie in movies:
        output.append({
            'movie_id': movie.movie_id,
            'title': movie.title
        })

    return jsonify({'movies': output})


@app.route('/get_movies_by_category', methods=['GET'])
@token_required
def get_movies_by_categories(current_user):
    auth = request.args
    genre = Genre.query.filter_by(genre=auth.get("category")).first()

    movie_genres = MovieGenre.query.filter_by(genre_id=genre.genre_id)

    output = []
    for movie_genre in movie_genres:
        movie = Movie.query.filter_by(movie_id=movie_genre.movie_id).first()

        output.append({
            'movie_id': movie.movie_id,
            'title': movie.title
        })

    return jsonify({'movies': output})


@app.route('/navigate', methods=['GET'])
@token_required
def navigate(current_user):
    title = request.args["title"]

    movie = Movie.query.filter_by(title=title).first()

    output = {
        'budget': '${:,.0f}'.format(movie.budget),
        'genres': movie.genres,
        'original_language': movie.original_language,
        'original_title': movie.original_title,
        'overview': movie.overview,
        'popularity': movie.popularity,
        'release_date': movie.release_date,
        'revenue': '${:,.0f}'.format(movie.revenue),
        'runtime': str(int(movie.runtime)) + ' minutes',
        'title': movie.title,
        'vote_average': movie.vote_average,
        'vote_count': movie.vote_count
    }

    return output


@app.route('/rent', methods=['POST'])
@token_required
def rent(current_user):
    auth = request.form
    movie = Movie.query.filter_by(title=auth.get("title")).first()

    movie_id = movie.movie_id
    rental_movie_id = Rental.query.filter_by(movie_id=movie_id).first()

    if rental_movie_id and rental_movie_id.paid is False:
        # returns 400 if current user has already rented the movie and hasn't paid for it
        return make_response(
            'You are currently renting this movie!',
            400
        )

    user_id = current_user.user_id
    time_now = datetime.now(timezone.utc)

    database.add_instance(Rental, movie_id=movie_id, user_id=user_id, date_start=time_now, paid=False)

    return jsonify('Movie ' + str(movie_id) + ' successfully rented!')


@app.route('/get_rentals', methods=['GET'])
@token_required
def get_rentals(current_user):
    rentals = Rental.query.filter_by(user_id=current_user.user_id)

    output = []
    for rental in rentals:
        output.append({
            'rental_id': rental.rental_id,
            'movie_id': rental.movie_id,
            'user_id': rental.user_id,
            'date_start': rental.date_start,
            'date_end': rental.date_end,
            'paid': rental.paid
        })

    return jsonify({'rentals': output})


@app.route('/return_movie', methods=['POST'])
@token_required
def return_movie(current_user):
    auth = request.form
    rental = Rental.query.filter_by(rental_id=auth.get("rental_id")).first()
    date_end = datetime.now(timezone.utc)
    data = {'date_end': date_end, 'paid': True}

    instance = Rental.query.filter_by(rental_id=rental.rental_id).all()[0]

    for attr, new_value in data.items():
        setattr(instance, attr, new_value)
    commit_changes()

    return jsonify('Rental ' + str(rental.rental_id) + ' successfully returned!')


@app.route('/get_charge', methods=['GET'])
@token_required
def get_charge(current_user):
    rentals = database.get_all(Rental)

    charge = 0
    for rental in rentals:
        if rental.paid is False:
            date_start = rental.date_start
            date_end = datetime.now(timezone.utc).date()
            delta = date_end - date_start
            days = delta.days

            for i in range(days + 1):
                if i <= 2:
                    charge += 1
                if i > 2:
                    charge += 0.5

    return jsonify({'charge': '€{:,.1f}'.format(charge)})
