from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField,IntegerField,StringField,TextAreaField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit7 = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit8 = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CreateForm(FlaskForm):
    movie_name = TextField('Movie Name')
    cast1 = TextField('Cast 1')
    cast2 = TextField('Cast 2')
    cast3 = TextField('Cast 3')
    date = TextField('Date')
    rating = TextField('Rating')
    summary = TextAreaField('Summary')
    genre = TextField('Genre')
    submit = SubmitField('Add Movie')

class UpdateForm(FlaskForm):
    movie_name = TextField('Movie Name')
    cast1 = TextField('Cast 1')
    cast2 = TextField('Cast 2')
    cast3 = TextField('Cast 3')
    date = TextField('Date')
    rating = TextField('Rating')
    summary = TextAreaField('Summary')
    genre = TextField('Genre')
    submit = SubmitField('Update')

class SearchForm(FlaskForm):
    search = StringField('')
    submit1 = SubmitField('Search')

class ActorForm(FlaskForm):
    actor_name = TextField('Actor Name')
    born_on = TextField('Born On')
    star_sign = TextField('Star Sign')
    bio = TextAreaField('Bio')
    submit2 = SubmitField('Add Actor')

class UpdateActorForm(FlaskForm):
    actor_name = TextField('Actor Name')
    born_on = TextField('Born On')
    star_sign = TextField('Star Sign')
    bio = TextAreaField('Bio')
    submit3 = SubmitField('Update Actor')

class ActorPairForm(FlaskForm):
    actor1 = TextField("First Artist")
    actor2 = TextField("Second Artist")
    submit4 = SubmitField('Go')
