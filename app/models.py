from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

acts = db.Table('acts',
	db.Column('movie_id',db.Integer,db.ForeignKey('movie.movie_id')),
	db.Column('actor_id',db.Integer,db.ForeignKey('actor.actor_id'))
	)

genres = db.Table('genres',
	db.Column('genre_id',db.Integer,db.ForeignKey('genre.genre_id')),
	db.Column('movie_id',db.Integer,db.ForeignKey('movie.movie_id'))
	)

likes = db.Table('likes',
	db.Column('id',db.Integer,db.ForeignKey('user.id')),
	db.Column('pair_id',db.Integer,db.ForeignKey('pair.pair_id'))
	)

class Actor(db.Model):
	actor_id = db.Column(db.Integer, primary_key=True)
	actor_name = db.Column(db.String(64), index=True)
	born_on = db.Column(db.String(64))
	star_sign = db.Column(db.String(64))
	bio = db.Column(db.String(250))
	acts_in = db.relationship('Movie', secondary=acts, backref=db.backref('cast'))

	def __repr__(self):
		return '<Actor {}>'.format(self.actor_name) 

class Movie(db.Model):
	movie_id = db.Column(db.Integer, primary_key=True)
	movie_name = db.Column(db.String(64), index=True)
	date = db.Column(db.String(64))
	rating = db.Column(db.String(64))
	summary = db.Column(db.String(250))
	has_genre = db.relationship('Genre', secondary=genres, backref=db.backref('movie'))

	def __repr__(self):
		return '<Movie {}>'.format(self.movie_name)  

class Genre(db.Model):
	genre_id = db.Column(db.Integer, primary_key=True)
	genre_name = db.Column(db.String(64), index=True)

	def __repr__(self):
		return '<Genre {}>'.format(self.genre_name) 

class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User {}>'.format(self.username) 

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Pair(db.Model):
	pair_id = db.Column(db.Integer, primary_key=True)
	actor1_id = db.Column(db.Integer)
	actor2_id = db.Column(db.Integer)
	upvotes = db.Column(db.Integer)
	liked_by = db.relationship('User', secondary=likes, backref=db.backref('Popularity'))

	def __repr__(self):
		return '<Pair {}, Upvotes {}>'.format(self.pair_id,self.upvotes) 


