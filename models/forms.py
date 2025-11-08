from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, FloatField
from wtforms.validators import Email, Length, InputRequired

class RegForm(FlaskForm):
    email = StringField('Email',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=20)])
    name = StringField('Name')

class BookForm(FlaskForm):
    check_in_date = DateTimeField('check_in_date',  validators=[InputRequired()])
    # total_cost = FloatField('total_cost', validators=[InputRequired(), Length(min=5, max=20)])
