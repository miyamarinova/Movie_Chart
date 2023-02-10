from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import LargeBinary
from wtforms import StringField, SubmitField
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
db = SQLAlchemy(app)

API_KEY = 'e079a3ae007263d6d3ffd3346fd221ce'
MOVIE_DB_SEARCH_URL = f'https://api.themoviedb.org/3/search/movie?api_key='
MOVIE_DB_DETAIL_URL = f"https://api.themoviedb.org/3/movie"
MOVIE_DB_IMG_URL = "https://image.tmdb.org/t/p/w500"

class RatingForm(FlaskForm):
    rating = StringField('Your Rating out of 10 e.g 7.5')
    review = StringField('Your Review')
    done = SubmitField('Done')

class NewMovieForm(FlaskForm):
    title = StringField('Movie Title')
    add = SubmitField('Add Movie')

#Create a new Table
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250), nullable=True)
    img_url = image = db.Column(db.String(500), nullable=True)

db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/update", methods=["GET", "POST"])
def update():
    form = RatingForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)

@app.route('/delete')
def delete_movie():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=["GET", "POST"])
def add_movie():
    form = NewMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(f'{MOVIE_DB_SEARCH_URL}{API_KEY}&query={movie_title}')
        data = response.json()

        return render_template('select.html', movies=data['results'])
    return render_template("add.html", form=form)


@app.route('/find', methods=["GET", "POST"])
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_DETAIL_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        movie = Movie(
            title=data['title'],
            year=data['release_date'].split('-')[0],
            img_url=f"{MOVIE_DB_IMG_URL}{data['poster_path']}",
            description=data['overview']
        )
        db.session.add(movie)
        db.session.commit()
        print(movie.img_url)
        return redirect(url_for('update', id=movie.id, movie=movie))


if __name__ == '__main__':
    app.run(debug=True)
