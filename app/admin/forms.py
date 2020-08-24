from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import SelectField

from ..models import Item, Unit, Shelf, Container
from ..validators import AfterDate

class ItemForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    unit = QuerySelectField(query_factory=lambda: Unit.query.all(), get_label="name")
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')

# class ItemDetailedLocForm(FlaskForm):


#     shelf = QuerySelectField(query_factory=lambda: Shelf.query.filter_by(unit_id), get_label="name")
#     submit = SubmitField('Submit')

class ReservationForm(FlaskForm):
    reason = StringField('Reason for Reservation', validators=[DataRequired()])
    fromDate = DateField('Date Needed', validators=[DataRequired(), AfterDate('Today', message='Must be after current date.')])
    toDate = DateField('Date Returning', validators=[DataRequired(), AfterDate('fromDate'), AfterDate('Today', message='Must be after current date.')])
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

class UnitForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AssignUnitForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    unit = QuerySelectField(query_factory=lambda: Unit.query.all(), get_label="name")
    submit = SubmitField('Submit')

class ShelfContainerForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ShelfContainerLocationUnknownForm(ShelfContainerForm):
    unit = QuerySelectField(query_factory=lambda: Unit.query.all(), get_label="name")
    submit = SubmitField('Submit')

class AssignShelfForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    shelf = SelectField('Shelf', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class AssignContainerForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    container = QuerySelectField(query_factory=lambda: Container.query.all(), get_label="name")
    submit = SubmitField('Submit')

