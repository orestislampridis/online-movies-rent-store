import configparser
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('ini/example.ini')

app.config['SQLALCHEMY_DATABASE_URI'] = config['app']['db_url']
app.secret_key = config['app']['secret_key']

db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)


# decorator for verifying the JWT
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


@app.route('/create_user', methods=['POST'])
def create_user():
    auth = request.form

    email = auth.get("email")
    password = bcrypt.generate_password_hash(auth.get("password")).decode('utf-8')
    first_name = auth.get("first_name")
    last_name = auth.get("last_name")

    conn = db.engine.raw_connection()
    cur = conn.cursor()

    sql = 'INSERT INTO "user" (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)'
    cur.execute(sql, (email, password, first_name, last_name))

    conn.commit()

    cur.close()
    conn.close()
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
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.secret_key)

        return make_response(jsonify({'token': token}), 201)

    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'})


@app.route('/get_all_movie_titles', methods=['GET'])
@token_required
def movies(current_user):
    movies = Movie.query.all()

    output = []
    for movie in movies:
        output.append({
            'movie_id': movie.movie_id,
            'title': movie.title
        })

    return jsonify({'movies': output})


@app.route('/get_movies_by_category', methods=['GET'])
@token_required
def categories(current_user):
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
    title = request.form["title"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT movie_id FROM movie WHERE title = %s'
    cur.execute(sql, (title,))

    movie_id = cur.fetchone()[0]
    user_id = current_user.user_id
    time_now = datetime.now(timezone.utc)

    sql = 'INSERT INTO rental (movie_id, user_id, date_start, paid) VALUES (%s, %s, %s, %s)'
    cur.execute(sql, (movie_id, user_id, time_now, False))

    conn.commit()

    cur.close()
    conn.close()
    return jsonify('Movie ' + str(movie_id) + ' successfully rented!')


@app.route('/get_charge', methods=['GET'])
@token_required
def get_charge(current_user):
    title = request.form["title"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT movie_id FROM movie WHERE title = %s'
    cur.execute(sql, (title,))

    movie_id = cur.fetchone()[0]
    user_id = current_user.user_id
    time_now = datetime.now(timezone.utc)

    sql = 'INSERT INTO rental (movie_id, user_id, date_start, paid) VALUES (%s, %s, %s, %s)'
    cur.execute(sql, (movie_id, user_id, time_now, False))

    conn.commit()

    cur.close()
    conn.close()
    return jsonify('Movie ' + str(movie_id) + ' successfully rented!')


if __name__ == '__main__':
    app.run(debug=True)
