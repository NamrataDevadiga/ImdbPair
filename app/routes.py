from flask import Flask, render_template, url_for, flash,redirect
from app import db, app
from app.forms import CreateForm,UpdateForm,SearchForm,ActorForm,UpdateActorForm,ActorPairForm,LoginForm,RegistrationForm
from app.models import *
from collections import Counter
from flask_login import current_user, login_user, logout_user, login_required
import operator


flag = 0
if flag==0:
	db.create_all()

def get_movie(actor_id,genre_id):
	final_genre_list = []
	actor_data = Actor.query.filter_by(actor_id=actor_id).first()
	movie_list_1 = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all()
	genre_data = Genre.query.filter_by(genre_id=genre_id).first()
	movie_list_2 = Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all()

	for i in movie_list_1:
		for j in movie_list_2:
			if i.movie_id==j.movie_id:
				final_genre_list.append((i.movie_id,i.movie_name))
	return final_genre_list

def get_genres(id):
	final_genre_list = []
	actor_data = Actor.query.filter_by(actor_id=id).first()
	movie_list = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all()
	for i in movie_list:
		movie_data = Movie.query.filter_by(movie_id=i.movie_id).first()
		genre_list = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all()
		for j in genre_list:
			final_genre_list.append((j.genre_id,j.genre_name))
	counts =  dict(Counter(final_genre_list))
	final_genre_list = []
	for i in sorted(counts,key=counts.get,reverse=True):
		final_genre_list.append(i)
	return final_genre_list

def get_common_movies(id1,id2):
	final_movie_list = []
	actor1_data = Actor.query.filter_by(actor_id=id1).first()
	actor2_data = Actor.query.filter_by(actor_id=id2).first()
	movie_list1 = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor1_data.actor_id).all()
	movie_list2 = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor2_data.actor_id).all()
	for i in movie_list1:
		for j in movie_list2:
			if i.movie_id==j.movie_id:
				final_movie_list.append(i)
	return final_movie_list

def get_costars(id1):
	id2 = int(id1)
	final_costar_list = {}
	actor_data = Actor.query.filter_by(actor_id=id1).first()
	movie_list = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all()
	for i in movie_list:
		coactor_data = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == i.movie_id).all()
		for j in coactor_data:
			if j.actor_id!=id2:
				if not j in final_costar_list:
					final_costar_list[j] = 1
				else:
					final_costar_list[j] += 1
	final_costar = max(final_costar_list.items(), key=operator.itemgetter(1))[0]
	actor2_data = Actor.query.filter_by(actor_id=final_costar.actor_id).first() 
	final_movie_list=get_common_movies(actor_data.actor_id,actor2_data.actor_id)
	return (final_costar,final_movie_list)


def get_popular_pair(id1):
	actor1_id = int(id1)
	final_pairs = {}
	pair_data1 = Pair.query.filter_by(actor1_id=id1).all()
	pair_data2 = Pair.query.filter_by(actor2_id=id1).all()
	for i in pair_data1:
		actor2_id = i.actor2_id
		j = (actor1_id,actor2_id)
		if j in final_pairs:
			final_pairs[j] += i.upvotes
		else:
			final_pairs[j] = i.upvotes
	for i in pair_data2:
		actor2_id = i.actor1_id
		j = (actor1_id,actor2_id)
		if j in final_pairs:
			final_pairs[j] += i.upvotes
		else:
			final_pairs[j] = i.upvotes

	if len(final_pairs) == 0:
		return None

	final_costar_id = max(final_pairs.items(), key=operator.itemgetter(1))[0][1] #returns id in int of popular costar
	actor1_data = Actor.query.filter_by(actor_id=id1).first()
	actor2_data = Actor.query.filter_by(actor_id=str(final_costar_id)).first()
	final_movie_list1=get_common_movies(actor1_data.actor_id,actor2_data.actor_id)
	return (actor2_data,final_movie_list1)

def get_autocomplete():
	movie_list = []
	movie_data = Movie.query.all()
	for i in movie_data:
		movie_list.append(i.movie_name)
	return movie_list

@app.route('/login',methods=['GET', 'POST'])
def login():

	error = None
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form7 = LoginForm()
	if form7.validate_on_submit():
		user = User.query.filter_by(username=form7.username.data).first()
		if user is None or not user.check_password(form7.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user)
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form7=form7, form1=form1)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

	error = None
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form8 = RegistrationForm()
	if form8.validate_on_submit():
		user = User(username=form8.username.data, email=form8.email.data)
		user.set_password(form8.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form8=form8, form1=form1)

@app.route('/',methods=['GET', 'POST'])
@login_required
def index():

	error = None
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	
	form4 = ActorPairForm()
	actor_autocomplete = get_autocomplete()
	if form4.submit4.data and form4.validate_on_submit():

		if form4.actor1.data == '':
			flash('Enter First Artist Name')
		elif form4.actor2.data == '':
			flash('Enter Second Artist Name')
		else:
			actor1 = form4.actor1.data.lower().title()
			actor2 = form4.actor2.data.lower().title()
			actor1_data = Actor.query.filter_by(actor_name=actor1).first()
			actor2_data = Actor.query.filter_by(actor_name=actor2).first()
			if actor1==actor2:
				flash('Both Artist cannot be same!')
			elif actor1_data and actor2_data:
				final_movie_list=get_common_movies(actor1_data.actor_id,actor2_data.actor_id)
				if final_movie_list:
					return render_template('results.html',form1=form1,actor1=actor1_data,actor2=actor2_data,movies=final_movie_list)
				else:
					flash('No Results!')
			elif actor1_data is None:
				flash('Artist 1 not found')
			else: 
				flash('Artist 2 not found')

	return render_template('index.html',form4=form4,form1=form1,actor_autocomplete=actor_autocomplete)

@app.route('/results/<id1>/<id2>',methods=['GET', 'POST'])
@login_required
def results(id1,id2):
	error = None
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	actor1_data = Actor.query.filter_by(actor_id=id1).first()
	actor2_data = Actor.query.filter_by(actor_id=id2).first()
	final_movie_list=get_common_movies(actor1_data.actor_id,actor2_data.actor_id)
	
	return render_template('results.html',form1=form1,actor1=actor1_data,actor2=actor2_data,movies=final_movie_list)

@app.route('/moviehome',methods=['GET', 'POST'])
def moviehome():

	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	return render_template('moviehome.html',form1=form1,movies=Movie.query.all())

@app.route('/actorhome',methods=['GET', 'POST'])
def actorhome():
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	return render_template('actorhome.html',form1=form1,actors=Actor.query.all())


@app.route('/movie/<id>',methods=['GET', 'POST'])
def movie(id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	return render_template('movie.html',form1=form1,movie=Movie.query.filter_by(movie_id=id).first(), id=id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == id).all())

@app.route('/actor/<id>',methods=['GET', 'POST'])
def actor(id):
	final_genre_list = get_genres(id)
	final_costar_list = get_costars(id)
	popular = get_popular_pair(id)

	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	return render_template('actor.html',form1=form1,id=id, actor=Actor.query.filter_by(actor_id=id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():

	error = None
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	
	form = CreateForm()
	if form.submit.data and form.validate_on_submit():

		if form.movie_name.data == '':
			flash('ERROR: Movie name is missing!!')
		else:
			m1 = Movie(movie_name=form.movie_name.data,date=form.date.data,rating=form.rating.data,summary=form.summary.data)
			db.session.add(m1)
			db.session.commit()
			
			if form.cast1.data != '':
				if not Actor.query.filter_by(actor_name=form.cast1.data).first():
					a1 = Actor(actor_name=form.cast1.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a1)
				else:
					a1 = Actor.query.filter_by(actor_name=form.cast1.data).first()
				db.session.commit()
				a1.acts_in.append(m1)

			if form.cast2.data != '':
				if not Actor.query.filter_by(actor_name=form.cast2.data).first():
					a2 = Actor(actor_name=form.cast2.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a2)
				else:
					a2 = Actor.query.filter_by(actor_name=form.cast2.data).first()
				db.session.commit()
				a2.acts_in.append(m1)

			if form.cast3.data != '':
				if not Actor.query.filter_by(actor_name=form.cast3.data).first():
					a3 = Actor(actor_name=form.cast3.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a2) 
				else:
					a3 = Actor.query.filter_by(actor_name=form.cast3.data).first()
				db.session.commit()
				a3.acts_in.append(m1)
			
			db.session.commit()

			if form.genre.data != '':
				if not Genre.query.filter_by(genre_name=form.genre.data).first():
					g = Genre(genre_name=form.genre.data)
					db.session.add(g)
				else:
					g = Genre.query.filter_by(genre_name=form.genre.data).first()

				db.session.commit()
				m1.has_genre.append(g)

			db.session.commit()

			flash('You have successfully added a movie')
			form4 = ActorPairForm()
			actor_autocomplete = get_autocomplete()
			return render_template('index.html',form4=form4,form1=form1,actor_autocomplete=actor_autocomplete)

	return render_template('create.html',form=form,form1=form1)

@app.route('/delete/<id>',methods=['GET','POST'])
def delete(id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	
	movie_id = int(id)
	movie = db.session.query(Movie).get(movie_id)
	sql = 'DELETE FROM acts WHERE movie_id='+id+';'
	db.engine.execute(sql)
	db.session.commit()
	sql = 'DELETE FROM movie WHERE movie_id='+id+';'
	db.engine.execute(sql)
	db.session.commit()
	flash ("Movie Deleted!")
	return render_template('moviehome.html', form1=form1, movies=Movie.query.all())

@app.route('/upvote/<actorid1>/<actorid2>/<userid>',methods=['GET','POST'])
@login_required
def upvote(actorid1,actorid2,userid):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	
	actor1_id = int(actorid1)
	actor2_id = int(actorid2)
	user_id = int(userid)

	actor1_data = Actor.query.filter_by(actor_id=actorid1).first()
	actor2_data = Actor.query.filter_by(actor_id=actorid2).first()
	final_movie_list=get_common_movies(actor1_data.actor_id,actor2_data.actor_id)

	user_data = User.query.filter_by(id=user_id).first()
	pair_data1 = Pair.query.filter_by(actor1_id=actor1_id,actor2_id=actor2_id).first()
	pair_data2 = Pair.query.filter_by(actor1_id=actor2_id,actor2_id=actor1_id).first()
	if pair_data1==None and pair_data2==None:
		p1 = Pair(actor1_id=actor1_id,actor2_id=actor2_id,upvotes=1)
		db.session.add(p1)
		db.session.commit()
		pair_data = Pair.query.filter_by(actor1_id=actor1_id,actor2_id=actor2_id).first()
		pair_data.liked_by.append(user_data)
		db.session.commit()
	elif pair_data1!=None and pair_data2==None:
		sql = 'SELECT * FROM likes WHERE id='+str(user_id)+' and pair_id='+str(pair_data1.pair_id)+';'
		invalid = db.engine.execute(sql)
		db.session.commit()
		a = len(invalid.fetchall())
		if a==0:
			upvotes = pair_data1.upvotes
			upvotes += 1
			pair_data1.upvotes = upvotes
			pair_data1.liked_by.append(user_data)
			db.session.commit()
			flash('Your vote has been submitted!')
		else:
			flash('You cant wont for same pair twice!')
	elif pair_data1==None and pair_data2!=None:
		sql = 'SELECT * FROM likes WHERE id='+str(user_id)+' and pair_id='+str(pair_data2.pair_id)+';'
		invalid = db.engine.execute(sql)
		db.session.commit()
		a = len(invalid.fetchall())
		if a==0:
			upvotes = pair_data2.upvotes
			upvotes += 1
			pair_data2.upvotes = upvotes
			pair_data2.liked_by.append(user_data)
			db.session.commit()
			flash('Your vote has been submitted!')
		else:
			flash('You cant wont for same pair twice!')

	return render_template('results.html',form1=form1,actor1=actor1_data,actor2=actor2_data,movies=final_movie_list)

@app.route('/update/<id>',methods=['GET','POST'])
@login_required
def update(id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	form = UpdateForm()
	if form.submit.data and form.validate_on_submit():
		movie_id = int(id)
		movie_name = form.movie_name.data
		date = form.date.data
		cast1 = form.cast1.data
		cast2 = form.cast2.data
		cast3 = form.cast3.data
		rating = form.rating.data
		summary = form.summary.data
		genre = form.genre.data

		movie_update = Movie.query.filter_by(movie_id=movie_id).first()

		if movie_name=='' and date=='' and cast1=='' and cast2=='' and cast3=='' and rating=='' and summary=='' and genre=='':
			flash('No data entered to update movie')
		else:
			if date!='':
				movie_update.date = date
			if movie_name!='':
				movie_update.movie_name = movie_name
			if rating!='':
				movie_update.rating = rating
			if summary!='':
				movie_update.summary = summary
			if cast1!='':
				if not Actor.query.filter_by(actor_name=cast1).first():
					a1 = Actor(actor_name=form.cast1.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a1)
				else:
					a1 = Actor.query.filter_by(actor_name=cast1).first()
				db.session.commit()
				a1.acts_in.append(movie_update)
			if cast2!='':
				if not Actor.query.filter_by(actor_name=cast2).first():
					a2 = Actor(actor_name=form.cast2.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a2)
				else:
					a2 = Actor.query.filter_by(actor_name=cast2).first()
				db.session.commit()
				a2.acts_in.append(movie_update)
			if cast3!='':
				if not Actor.query.filter_by(actor_name=cast3).first():
					a3 = Actor(actor_name=form.cast3.data,born_on=None,star_sign=None,bio=None)
					db.session.add(a3)
				else:
					a3 = Actor.query.filter_by(actor_name=cast3).first()
				db.session.commit()
				a3.acts_in.append(movie_update)
			if genre!='':
				if not Genre.query.filter_by(genre_name=genre).first():
					g = Genre(genre_name=genre)
					db.session.add(g)
				else:
					g = Genre.query.filter_by(genre_name=genre).first()

				db.session.commit()
				movie_update.has_genre.append(g)

			db.session.commit()
			flash('Data Updated')
			return render_template('moviehome.html', form1=form1, movies=Movie.query.all())

	return render_template('update.html',form1=form1,form=form,movies=Movie.query.all(), id=id)

@app.route('/addactor', methods=['GET', 'POST'])
@login_required
def addactor():

	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	
	form2 = ActorForm()
	if form2.submit2.data and form2.validate_on_submit():

		if form2.actor_name.data == '':
			flash ("ERROR: YOU NEED TO ENTER A NAME FOR THE ACTOR")
		else:
			a = Actor(actor_name=form2.actor_name.data,born_on=form2.born_on.data,star_sign=form2.star_sign.data,bio=form2.bio.data)
			db.session.add(a)
			db.session.commit()
			flash ("Actor added Successfully!")
			return render_template('moviehome.html',form1=form1,movies=Movie.query.all())

	return render_template('addactor.html',form1=form1,form2=form2)

@app.route('/genre',methods=['GET','POST'])
def genre():
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)
	return render_template('genre.html',form1=form1,genres=Genre.query.all())


@app.route('/updateactor/<id>',methods=['GET','POST'])
@login_required
def updateactor(id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	form3 = UpdateActorForm()
	if form3.submit3.data and form3.validate_on_submit():
		actor_id = int(id)
		actor_name = form3.actor_name.data
		born_on = form3.born_on.data
		star_sign = form3.star_sign.data
		bio = form3.bio.data
		actor_update = Actor.query.filter_by(actor_id=actor_id).first()
		if actor_name=='' and born_on=='' and star_sign=='' and bio=='':
			flash ("YOU NEED TO ENTER SOME INFORMATION TO DO AN UPDATE")
		else:
			if actor_name != '':
				actor_update.actor_name = actor_name
			if born_on != '':
				actor_update.born_on = born_on
			if star_sign != '':
				actor_update.star_sign = star_sign
			if bio != '':
				actor_update.bio = bio
			db.session.commit()
			flash ("Actor information Updated!")
			return render_template('actorhome.html',form1=form1,actors=Actor.query.all())
	return render_template('updateactor.html',form1=form1,form3=form3,movies=Movie.query.all(), id=id)

@app.route('/actorgenre/<id>',methods=['GET','POST'])
def actorgenre(id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	final_genre_list = get_genres(id)
	return render_template('actorgenre.html',form1=form1,id=id,actor=Actor.query.filter_by(actor_id=id).first(),genres=final_genre_list)

@app.route('/genremovie/<genre_id>',methods=['GET','POST'])
def genremovie(genre_id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	return render_template('genremovie.html',form1=form1,genre_id=genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_id).all())

@app.route('/actorgenremovie/<genre_id>/<actor_id>',methods=['GET','POST'])
def actorgenremovie(genre_id,actor_id):
	form1 = SearchForm()
	if form1.submit1.data and form1.validate_on_submit():
		data = form1.search.data.lower().title()
		movie_data = Movie.query.filter_by(movie_name=data).first()
		actor_data = Actor.query.filter_by(actor_name=data).first()
		genre_data = Genre.query.filter_by(genre_name=data).first()
		if movie_data:
			return render_template('movie.html',form1=form1,movie=movie_data, id=movie_data.movie_id, actors = Actor.query.join(acts).join(Movie).filter(acts.c.movie_id == movie_data.movie_id).all(),genres = Genre.query.join(genres).join(Movie).filter(genres.c.movie_id == movie_data.movie_id).all())
		elif actor_data:
			final_genre_list = get_genres(actor_data.actor_id)
			final_costar_list = get_costars(actor_data.actor_id)
			popular = get_popular_pair(actor_data.actor_id)
			return render_template('actor.html',form1=form1,id=actor_data.actor_id, actor=Actor.query.filter_by(actor_id=actor_data.actor_id).first(), movies = Movie.query.join(acts).join(Actor).filter(acts.c.actor_id == actor_data.actor_id).all(),genres=final_genre_list,costars=final_costar_list,popular=popular)
		elif genre_data:
			return render_template('genremovie.html',form1=form1,genre_id=genre_data.genre_id,movies=Movie.query.join(genres).join(Genre).filter(genres.c.genre_id == genre_data.genre_id).all())
		else:
			return render_template('notfound.html',form1=form1)

	return render_template('actorgenremovie.html',form1=form1,genre_id=genre_id,actor_id=actor_id,movies=get_movie(actor_id,genre_id))

