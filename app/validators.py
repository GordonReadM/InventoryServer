from wtforms import ValidationError
from datetime import date 

class Length(object):
	def __init__(self, min=-1, max=-1, message=None):
		self.min = min
		self.max = max
		if not message:
			message = u'Field must be between %i and %i characters long.' % (min, max)
		self.message = message

	def __call__(self, form, field):
		l = field.data and len(field.data) or 0
		if l < self.min or self.max != -1 and l > self.max:
			raise ValidationError(self.message)

class Password(object):
	def __init__(self, message=None):
		if not message:
			message = u'Field must contain a number, a capital letter, a lowercase letter, and one of the following: $, !, ?, %, #, @, &.'
		self.message = message

	def __call__(self, form, field):
		required_symbols = ['$', '!', '?', '%', '#', '@', '&']
		contains_symbol = False
		for c in required_symbols:
			if c in field.data:
				contains_symbol = True

		if not (any(c.isupper() for c in field.data) and any(c.isdigit() for c in field.data) and any(c.islower() for c in field.data) and contains_symbol):
			raise ValidationError(self.message)

class AfterDate(object):
	def __init__(self, fieldname, message=None):
		self.fieldname = fieldname
		if not message:
			message = u'From Date must be before To Date.'
		self.message = message

	def __call__(self, form, field):
		#print ('\n\n\n' + field.data + '\n\n\n')
		if self.fieldname == 'Today':
			fromDateFieldData = date.today()
		else:
			try:
				fromDateFieldData = form[self.fieldname].data
			except KeyError:
				raise ValidationError(field.gettext(u'Invalid field name: %s.') % self.fieldname)
		if field.data < fromDateFieldData:
			raise ValidationError(self.message)