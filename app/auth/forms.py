from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.fields.html5 import DateField, EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Item, Brother
from ..validators import Length, Password, AfterDate

class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
    email = EmailField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4,max=20)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password'),
                                        Password(),
                                        Length(min=6,max=16)
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if Brother.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if Brother.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')

class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReservationForm(FlaskForm):
    reason = StringField('Reason for Reservation', validators=[DataRequired()])
    fromDate = DateField('Date Needed', validators=[DataRequired(), AfterDate('Today')])
    toDate = DateField('Date Returning', validators=[DataRequired(), AfterDate('fromDate'), AfterDate('Today')])
    submit = SubmitField('Submit')

class ReservationAddForm(ReservationForm):
    """
    Form for admin to add or edit a role
    """
    hasItem = False

    item = QuerySelectField(query_factory=lambda: Item.query.all(), get_label="name")
    submit = SubmitField('Submit')

class ReservationAddForItemForm(ReservationForm):
    """
    Form for admin to add or edit a role
    """

    hasItem = True
    item = None

class ReservationEditForm(ReservationForm):
    """
    Form for admin to add or edit a role
    """
    item = None

class ResetPasswordGetEmailForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_new_password'),
                                        Password(),
                                        Length(min=6,max=16)
                                        ])
    confirm_new_password = PasswordField('Confirm New Password')
    submit = SubmitField('Confirm')