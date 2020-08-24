from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class Brother(UserMixin, db.Model):
	"""
	Create an Brothers table
	"""

	# Ensures table will be named in plural and not in singular
	# as is the name of the model
	__tablename__ = 'brothers'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(60), index=True, unique=True)
	username = db.Column(db.String(60), index=True, unique=True)
	first_name = db.Column(db.String(60), index=True)
	last_name = db.Column(db.String(60), index=True)
	password_hash = db.Column(db.String(128))
	is_admin = db.Column(db.Boolean)
	email_confirmed = db.Column(db.Boolean)
	reservations = db.relationship('Reservation', backref='brother', lazy='dynamic')

	@property
	def password(self):
		"""
		Prevent pasword from being accessed
		"""
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		"""
		Set password to a hashed password
		"""
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<Brother: {}>'.format(self.first_name)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
	return Brother.query.get(int(user_id))

class Item(db.Model):
	"""
	Create a Item table
	"""

	__tablename__ = 'items'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), unique=True)
	description = db.Column(db.String(200))
	quantity = db.Column(db.Integer)
	unit_id = db.Column(db.Integer, db.ForeignKey('storage_units.id'))
	shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'))
	container_id = db.Column(db.Integer, db.ForeignKey('containers.id'))
	reservations = db.relationship('Reservation', backref='item', lazy='dynamic')

	def __repr__(self):
		return '<Item: {}>'.format(self.name)

class Reservation(db.Model):
	"""
	Create a Reservations table
	"""

	__tablename__ = 'reservations'

	id = db.Column(db.Integer, primary_key=True)
	reason = db.Column(db.String(200))
	fromDate = db.Column(db.Date)
	toDate = db.Column(db.Date)
	reserved_by = db.Column(db.String(20))
	item_name = db.Column(db.String(60))
	approved = db.Column(db.Boolean, default=False)
	brother_id = db.Column(db.Integer, db.ForeignKey('brothers.id'))
	item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

	def __repr__(self):
		return '<Reservation: {}>'.format(self.reason)

class Unit(db.Model):
	"""
	Create a Units table
	"""

	__tablename__ = 'storage_units'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60))
	location = db.Column(db.String(60))
	shelves = db.relationship('Shelf', backref='unit', lazy='dynamic')
	items = db.relationship('Item', backref='unit', lazy='dynamic')
	units = db.relationship('Container', backref='unit', lazy='dynamic')

	def __repr__(self):
		return '<Unit: {}>'.format(self.name)

class Shelf(db.Model):
	"""
	Create a Shelves Table
	"""

	__tablename__ = 'shelves'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	unit_id = db.Column(db.Integer, db.ForeignKey('storage_units.id'))
	items = db.relationship('Item', backref='shelf', lazy='dynamic')
	units = db.relationship('Container', backref='shelf', lazy='dynamic')
	
	def __repr__(self):
		return '<Shelf: {}>'.format(self.name)

class Container(db.Model):

	__tablename__ = 'containers'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	unit_id = db.Column(db.Integer, db.ForeignKey('storage_units.id'))
	shelf_id = db.Column(db.Integer, db.ForeignKey('shelves.id'))
	items = db.relationship('Item', backref='container', lazy='dynamic')

	def __repr__(self):
		return 'Container: {}'.format(self.name)


