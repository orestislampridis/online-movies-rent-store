from video_club import db


# Database ORMs
class Movie(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True)
    budget = db.Column(db.BigInteger)
    genres = db.Column(db.Text)
    original_language = db.Column(db.Text)
    original_title = db.Column(db.Text)
    overview = db.Column(db.Text)
    popularity = db.Column(db.Float)
    release_date = db.Column(db.Text)
    revenue = db.Column(db.BigInteger)
    runtime = db.Column(db.Float)
    title = db.Column(db.Text)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)


class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.Text)


class MovieGenre(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, primary_key=True)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def to_json(self):
        return {"first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id


class Rental(db.Model):
    rental_id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    paid = db.Column(db.Boolean)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)

