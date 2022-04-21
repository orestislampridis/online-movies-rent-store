from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import jsonify, request, make_response
from API import app, bcrypt, database
from API.database import commit_changes
from API.models import Movie, User, Genre, MovieGenre, Rental
from API import db

# decorator for verifying the JWT
from API.read_dataset import read_dataset


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
        movie_df, movie_genre_df, genre_df = read_dataset(path_prefix='API/dataset/tmdb_5000_movies.csv')

        movie_df.to_sql(name='movie', con=db.engine, index_label='movie_id', if_exists='append', chunksize=1000)
        movie_genre_df.to_sql(name='movie_genre', con=db.engine, index='movie_id', if_exists='append', chunksize=1000)
        genre_df.to_sql(name='genre', con=db.engine, index_label='genre_id', if_exists='append', chunksize=1000)


# Will delete all your data, only use in case of emergency
@app.route('/reinitialize_tables', methods=['PATCH'])
def reinitialize_tables():
    db.drop_all()
    create_tables()


@app.route('/create_user', methods=['POST'])
def create_user():
    auth = request.json

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 400 if any email or / and password is missing
        return make_response(
            {'ok': False, 'message': 'email and / or password is missing'},
            400
        )

    email = auth.get("email")
    password = bcrypt.generate_password_hash(auth.get("password")).decode('utf-8')
    first_name = auth.get("first_name")
    last_name = auth.get("last_name")

    user = User.query.filter_by(email=auth.get("email")).first()

    if user:
        # returns 400 if current user email already exists
        return make_response({"ok": False, "message": "Current email already exists!"}, 400)

    database.add_instance(User, email=email, password=password, first_name=first_name, last_name=last_name)

    return make_response({"ok": True, "message": "User successfully created!"}, 201)


@app.route('/login', methods=['POST'])
def login():
    auth = request.json

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 400 if any email or / and password is missing
        return make_response(
            {'ok': False, 'message': 'email and / or password is missing'},
            400
        )

    user = User.query.filter_by(email=auth.get("email")).first()

    if not user:
        # returns 404 if user does not exist
        return make_response(
            {'ok': False, 'message': 'User does not exist'},
            404
        )

    if bcrypt.check_password_hash(user.password, auth.get("password")):
        token = jwt.encode({
            'user_id': user.user_id,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, app.secret_key)

        return make_response(jsonify({'token': token, 'ok': True}), 201)

    # returns 403 if password is wrong
    return make_response(
        {'ok': False, 'message': 'Could not verify. Incorrect password given'},
        403
    )


@app.route('/get_all_users', methods=['GET'])
@token_required
def get_all_users(current_user):
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

    if not auth or not auth.get('category'):
        # returns 400 if category is missing
        return make_response(
            {'ok': False, 'message': 'Category parameter is missing'},
            400
        )

    genre = Genre.query.filter_by(genre=auth.get("category")).first()

    if not genre:
        # returns 404 if genre does not exist
        return make_response(
            {'ok': False, 'message': 'Genre does not exist'},
            404
        )

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
    auth = request.args

    if not auth or not auth.get('title'):
        # returns 400 if title is missing
        return make_response(
            {'ok': False, 'message': 'Title parameter is missing'},
            400
        )

    title = auth.get("title")

    movie = Movie.query.filter_by(title=title).first()

    if not movie:
        # returns 404 if movie does not exist
        return make_response(
            {'ok': False, 'message': 'Movie does not exist'},
            404
        )

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
    auth = request.json

    if not auth or not auth.get('title'):
        # returns 400 if title is missing
        return make_response(
            {'ok': False, 'message': 'Body title is missing'},
            400
        )

    movie = Movie.query.filter_by(title=auth.get("title")).first()

    if not movie:
        # returns 404 if movie does not exist
        return make_response(
            {'ok': False, 'message': 'Movie does not exist'},
            404
        )

    movie_id = movie.movie_id
    rental_movie_id = Rental.query.filter_by(movie_id=movie_id, user_id=current_user.user_id).first()

    if rental_movie_id is not None and rental_movie_id.paid is False:
        # returns 400 if current user has already rented the movie and hasn't paid for it
        return make_response(
            {'ok': False, 'message': 'You are already renting this movie!'},
            400
        )

    user_id = current_user.user_id
    time_now = datetime.now(timezone.utc)

    database.add_instance(Rental, movie_id=movie_id, user_id=user_id, date_start=time_now, paid=False)

    return make_response(
        {'ok': True, 'message': str(movie.title) + ' successfully rented!'},
        200
    )


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
    auth = request.json

    if not auth or not auth.get('title'):
        # returns 400 if title is missing
        return make_response(
            {'ok': False, 'message': 'Body title is missing'},
            400
        )

    movie = Movie.query.filter_by(title=auth.get('title')).first()

    if not movie:
        # returns 404 if movie does not exist
        return make_response(
            {'ok': False, 'message': 'Movie does not exist'},
            404
        )

    rental = Rental.query.filter_by(movie_id=movie.movie_id, user_id=current_user.user_id, paid=False).first()

    if not rental:
        # returns 404 if rental does not exist
        return make_response(
            {'ok': False, 'message': 'You have not rented this movie!'},
            404
        )

    date_end = datetime.now(timezone.utc)
    data = {'date_end': date_end, 'paid': True}

    for attr, new_value in data.items():
        setattr(rental, attr, new_value)
    commit_changes()

    return make_response(
        {'ok': True,
         'message': str(movie.title) + ' (rental id: ' + str(rental.rental_id) + ')' + ' successfully returned!'},
        200
    )


@app.route('/get_charge', methods=['GET'])
@token_required
def get_charge(current_user):
    rentals = Rental.query.filter_by(user_id=current_user.user_id)

    charge = 0
    for rental in rentals:
        # Check if the user has already paid some of his rentals
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
