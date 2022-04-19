import configparser
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('ini/example.ini')

app.config['SQLALCHEMY_DATABASE_URI'] = config['app']['db_url']
app.secret_key = config['app']['secret_key']

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/movies', methods=['GET'])
def movies():
    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT title FROM movie;'
    cur.execute(sql)
    movie_titles = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(movie_titles)


@app.route('/categories', methods=['GET'])
def categories():
    category = request.args["category"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT genre_id FROM genre WHERE genre = %s;'
    cur.execute(sql, (category,))
    genre_id = cur.fetchone()

    sql = 'SELECT movie_id FROM movie_genre WHERE genre_id = %s;'
    cur.execute(sql, (genre_id,))
    movie_id = cur.fetchall()

    sql = 'SELECT title FROM movie WHERE movie_id = ANY(%s);'
    cur.execute(sql, (movie_id,))

    movie_titles = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(movie_titles)


@app.route('/navigate', methods=['GET'])
def navigate():
    title = request.args["title"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT * FROM movie WHERE title = %s;'

    cur.execute(sql, (title,))
    results = cur.fetchone()
    cur.close()
    conn.close()

    dict = {
        'budget': '${:,.0f}'.format(results[1]),
        'genres': results[2],
        'original_language': results[3],
        'original_title': results[4],
        'overview': results[5],
        'popularity': results[6],
        'release_date': results[7],
        'revenue': '${:,.0f}'.format(results[8]),
        'runtime': str(int(results[9])) + ' minutes',
        'title': results[10],
        'vote_average': results[11],
        'vote_count': results[12]
    }

    return dict


@app.route('/create_user', methods=['POST'])
def create_user():
    email = request.form["email"]
    password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()

    sql = 'INSERT INTO "user" (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)'
    cur.execute(sql, (email, password, first_name, last_name))

    conn.commit()

    cur.close()
    conn.close()
    return jsonify('User succesfully created!')


@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.form["email"]).first()
    if user:
        if bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return jsonify(user.to_json())

    return jsonify('Failed!')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return jsonify('User succesfully logged out!')


@app.route('/rent', methods=['POST'])
@login_required
def rent():
    title = request.form["title"]

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    sql = 'SELECT movie_id FROM movie WHERE title = %s'
    cur.execute(sql, (title,))

    if current_user.is_authenticated():
        movie_id = cur.fetchone()[0]
        user_id = current_user.get_id()
        time_now = datetime.now(timezone.utc)

        sql = 'INSERT INTO rental (movie_id, user_id, date_start) VALUES (%s, %s, %s)'
        cur.execute(sql, (movie_id, user_id, time_now))

    conn.commit()

    cur.close()
    conn.close()
    return jsonify('Movie ' + str(movie_id) + ' succesfully rented!')


if __name__ == '__main__':
    app.run(debug=True)
