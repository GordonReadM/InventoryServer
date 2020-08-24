from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_mail import Message

from . import admin
from .forms import *
from .. import db, mail
from ..models import Item, Reservation, Brother, Unit, Shelf, Unit, Container

def check_admin():
	"""
	Prevent non-admins from accessing the page
	"""
	if not current_user.is_admin:
		abort(403)

# Item Views

@admin.route('/items', methods=['GET', 'POST'])
@admin.route('/items/<int:type_code>/<int:object_id>', methods=['GET', 'POST'])
@login_required
def list_items(type_code=-1, object_id=None):
	"""
	List all items
	"""
	check_admin()

	shelf = Shelf()
	unit = Unit()
	if type_code == -1:
		items = Item.query.all()
	elif type_code == 0:
		items = Item.query.filter_by(shelf_id=object_id).all()
		shelf = Shelf.query.get(object_id)
		unit = Unit.query.filter_by(id=shelf.unit_id).first()
	elif type_code == 1:
		#item_id is 0 and brother_id is not
		items = Item.query.filter_by(unit_id=object_id).all()
		unit = Unit.query.get(object_id)

	for item in items:
		if item.shelf is not None and item.unit is None:
			if shelf.unit is None:
				item.shelf_id = None
				db.session.delete(item.shelf)
			item.unit_id = shelf.unit_id
			db.session.add(item)
			db.session.commit()

		# if item.unit_id:
		# 	item.unit = Unit.query.filter_by(id=item.unit_id).first()
		# else:
		# 	item.unit = None
		# if item.shelf_id:
		# 	item.shelf = Shelf.query.filter_by(id=item.shelf_id).first()
		# else:
		# 	item.shelf = None

	return render_template('admin/items/items.html',
						   items=items, shelf=shelf, unit=unit,
						   title="Items")

@admin.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
	"""
	Add a item to the database
	"""
	check_admin()

	add_item = True

	form = ItemForm()
	if form.validate_on_submit():
		item = Item(name=form.name.data,
						description=form.description.data,
						unit_id=form.unit.data.id,
						quantity=form.quantity.data)
		try:
			# add item to the database
			db.session.add(item)
			db.session.commit()
			flash('You have successfully added a new item.')
		except:
			# in case item name already exists
			flash('Error: item name already exists.', 'danger')

		# redirect to items page
		return redirect(url_for('admin.list_items'))

	# load item template
	return render_template('admin/items/item.html', action="Add",
						   add_item=add_item, form=form,
						   title="Add Item")

@admin.route('/items/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
	"""
	Edit a item
	"""
	check_admin()

	add_item = False

	item = Item.query.get_or_404(id)
	old_unit = item.unit_id
	form = ItemForm(obj=item)
	if form.validate_on_submit():
		item.name = form.name.data
		item.description = form.description.data
		item.unit_id = form.unit.data.id
		item.quantity = form.quantity.data
		if not old_unit == item.unit_id:
			item.shelf_id = None

		db.session.add(item)
		db.session.commit()
		flash('You have successfully edited the item.')

		# redirect to the items page
		return redirect(url_for('admin.list_items'))

	form.description.data = item.description
	form.name.data = item.name
	return render_template('admin/items/item.html', action="Edit",
						   add_item=add_item, form=form,
						   item=item, title="Edit Item")

@admin.route('/items/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_item(id):
	"""
	Delete a item from the database
	"""
	check_admin()

	item = Item.query.get_or_404(id)
	db.session.delete(item)
	db.session.commit()
	flash('You have successfully deleted the Item.')

	# redirect to the items page
	return redirect(url_for('admin.list_items'))

	return render_template(title="Delete Item")

@admin.route('/items/assign_unit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def assign_unit_item(item_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	item = Item.query.get_or_404(item_id)

	if len(Unit.query.all()) == 0:
		flash('There are no units.')
		return redirect(url_for('admin.list_items'))

	form = AssignUnitForm()

	if form.validate_on_submit():
		item.unit_id = form.unit.data.id

		try:
			db.session.add(item)
			db.session.commit()
		except:
			flash('Error: Unit was not assigned')

		flash('You have successfully assigned a unit to the item.')
		return redirect(url_for('admin.list_items'))

	# redirect to the items page
	return render_template('admin/units/unit.html',
						   object=item, title='Add Unit', form=form)

@admin.route('/items/assign_shelf/<int:item_id>', methods=['GET', 'POST'])
@login_required
def assign_shelf_item(item_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	item = Item.query.get_or_404(item_id)

	if item.unit is None:
		flash ('Please assign a Unit to the Item first')
		return redirect(url_for('admin.list_items'))

	shelves = Shelf.query.filter_by(unit_id=item.unit.id).all()
	if len(shelves) == 0:
		flash('There are no shelves in this unit. Add some shelves!')
		return redirect(url_for('admin.list_items'))

	shelves_with_no = [(shelf.id,shelf.name) for shelf in shelves]

	form = AssignShelfForm()
	form.shelf.choices = shelves_with_no

	if form.validate_on_submit():
		item.shelf_id = form.shelf.data

		try:
			db.session.add(item)
			db.session.commit()
		except:
			flash('Error: Shelf was not assigned')

		flash('You have successfully assigned a shelf to the item.')
		return redirect(url_for('admin.list_items'))

	# redirect to the items page
	return render_template('admin/shelves/shelf.html',
						   object=item, unit=item.unit, title='Add Shelf', form=form)

@admin.route('/items/assign_container/<int:item_id>', methods=['GET', 'POST'])
@login_required
def assign_container_item(item_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	item = Item.query.get_or_404(item_id)

	if len(Container.query.all()) == 0:
		flash('There are no containers.')
		return redirect(url_for('admin.list_items'))

	form = AssignContainerForm()

	if form.validate_on_submit():
		item.container_id = form.container.data.id

		try:
			db.session.add(item)
			db.session.commit()
		except:
			flash('Error: Container was not assigned')

		flash('You have successfully assigned a container to the item.')
		return redirect(url_for('admin.list_items'))

	# redirect to the items page
	return render_template('admin/containers/container.html',
						   item=item, title='Add Unit', form=form)

@admin.route('/reservations')
@admin.route('/reservations/<int:type_code>/<int:object_id>')
@login_required
def list_reservations(type_code=-1, object_id=0):
	check_admin()
	"""
	List all reservations
	"""

	item = Item()
	brother = Brother()
	if type_code == -1:
		reservations = Reservation.query.all()
	elif type_code == 0:
		reservations = Reservation.query.filter_by(item_id=object_id).all()
		item = Item.query.get(object_id)
	elif type_code == 1:
		#item_id is 0 and brother_id is not
		reservations = Reservation.query.filter_by(brother_id=object_id).all()
		brother = Brother.query.get(object_id)

	return render_template('admin/reservations/reservations.html',
						   reservations=reservations, title='Reservations', item=item, brother=brother)

@admin.route('/reservation/add', methods=['GET', 'POST'])
@admin.route('/reservation/add/<int:item_id>', methods=['GET', 'POST'])
@login_required
def add_reservation(item_id=0):
	"""
	Add a reservation to the database
	"""
	check_admin()

	add_reservation = True

	if item_id == 0:
		form = ReservationAddForm()
	else:
		form = ReservationAddForItemForm()
		form.item = Item.query.get(item_id)

	if form.validate_on_submit():
		reservation = Reservation(reason=form.reason.data,
					fromDate=form.fromDate.data,
					toDate=form.toDate.data,
					reserved_by=current_user.first_name + ' ' + current_user.last_name,
					item_name=form.item.data.name,
					item_id=form.item.data.id,
					brother_id=current_user.id)

		try:
			# add reservation to the database
			db.session.add(reservation)
			db.session.commit()
			flash('You have successfully added a new reservation for the %s.' % form.item.data.name)
		except:
			# in case reservation name already exists
			flash('Error: reservation name already exists.')

		# redirect to the reservations page
		return redirect(url_for('admin.list_reservations'))

	# load reservation template
	return render_template('admin/reservations/reservation.html', add_reservation=add_reservation,
						   form=form, title='Add Reservation')

@admin.route('/reservations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(id):
	"""
	Edit a reservation
	"""
	check_admin()

	add_reservation = False

	reservation = Reservation.query.get_or_404(id)
	form = ReservationEditForm(obj=reservation)
	form.item = reservation.item
	if form.validate_on_submit():
		reservation.reason = form.reason.data
		reservation.fromDate = form.fromDate.data
		reservation.toDate = form.toDate.data
		db.session.add(reservation)
		db.session.commit()
		flash('You have successfully edited the reservation.')

		# redirect to the reservations page
		return redirect(url_for('admin.list_reservations'))

	form.reason.data = reservation.reason
	form.fromDate.data = reservation.fromDate
	form.toDate.data = reservation.toDate
	return render_template('admin/reservations/reservation.html', add_reservation=add_reservation,
						   form=form, title="Edit Reservation", item=Item.query.filter_by(id=id).first())

@admin.route('/reservation/GrantApproval/<int:id>', methods=['GET', 'POST'])
@admin.route('/reservation/GrantApproval/<int:id>/<string:item>', methods=['GET', 'POST'])
@login_required
def approve_reservation(id, item=None):
	"""
	Add a reservation to the database
	"""
	check_admin()

	reservation = Reservation.query.get_or_404(id)

	reservation.approved = True
	db.session.add(reservation)
	db.session.commit()

	toFlash = 'You have successfully approved the reservation. An email notification has been sent to the reserving active.'
	html = '<p>Your reservation for the %s has been approved.</p>' % Item.query.get(reservation.item_id).name

	brother = Brother.query.get(reservation.brother_id)
	msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Your Reservation for %s' % reservation.item.name, recipients=[brother.email])
	mail.send(msg)

	flash(toFlash)

	if item is None:
		return redirect(url_for('admin.list_reservations'))
	else:
		return redirect(url_for('admin.list_reservations', item.id, item.name))

@admin.route('/reservation/RevokeApproval/<int:id>', methods=['GET', 'POST'])
@admin.route('/reservation/RevokeApproval/<int:id>/<string:item>', methods=['GET', 'POST'])
@login_required
def revoke_reservation(id, item=None):
	"""
	Add a reservation to the database
	"""
	check_admin()

	reservation = Reservation.query.get_or_404(id)

	reservation.approved = False
	db.session.add(reservation)
	db.session.commit()

	toFlash = 'You have successfully revoked approval for the reservation. An email notification has been sent to the reserving active.'
	html = '<p>Your reservation for the %s has been revoked.</p>' % Item.query.get(reservation.item_id).name

	brother = Brother.query.filter_by(id=reservation.brother_id).first()
	msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Your Reservation for %s' % reservation.item.name, recipients=[brother.email])
	mail.send(msg)

	flash(toFlash)

	if item is None:
		return redirect(url_for('admin.list_reservations'))
	else:
		return redirect(url_for('admin.list_reservations', item.id, item.name))

@admin.route('/reservations/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_reservation(id):
	"""
	Delete a reservation from the database
	"""
	check_admin()

	reservation = Reservation.query.get_or_404(id)
	db.session.delete(reservation)
	db.session.commit()
	flash('You have successfully deleted the reservation.')

	# redirect to the reservations page
	return redirect(url_for('admin.list_reservations'))

	return render_template(title="Delete Reservation")

@admin.route('/brothers')
@login_required
def list_brothers():
	"""
	List all employees
	"""
	check_admin()

	brothers = Brother.query.all()
	return render_template('admin/brothers/brothers.html',
						   brothers=brothers, title='Brothers', current_user=current_user)

@admin.route('/brothers/GrantAdmin/<int:id>', methods=['GET', 'POST'])
@login_required
def grant_admin(id):
	"""
	List all employees
	"""
	check_admin()

	brother = Brother.query.get_or_404(id)
	brother.is_admin = True
	db.session.add(brother)
	db.session.commit()


	toFlash = 'You have successfully granted admin access to %s. They have been sent an email.' % brother.first_name
	html = '<p>You have been made an admin on Alpha Gamma\'s Inventory website</p>'

	msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Admin status for Alpha Gamma Inventory', recipients=[brother.email])
	mail.send(msg)

	flash(toFlash)

	return redirect(url_for('admin.list_brothers'))

@admin.route('/brothers/RevokeAdmin/<int:id>', methods=['GET', 'POST'])
@login_required
def revoke_admin(id):
	"""
	List all employees
	"""
	check_admin()

	brother = Brother.query.get_or_404(id)
	brother.is_admin = False
	db.session.add(brother)
	db.session.commit()


	toFlash = 'You have successfully revoked admin access from %s. They have been sent an email.' % brother.first_name
	html = '<p>You have been removed as an admin on Alpha Gamma\'s Inventory website</p>'

	msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Admin status for Alpha Gamma Inventory', recipients=[brother.email])
	mail.send(msg)

	flash(toFlash)

	return redirect(url_for('admin.list_brothers'))

@admin.route('/brothers/RemoveBrother/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_brother(id):
	check_admin()

	brother = Brother.query.get_or_404(id)
	brother_reservations = Reservation.query.filter_by(brother_id=id).all()

	db.session.delete(brother)
	for reservation in brother_reservations:
		db.session.delete(reservation)

	db.session.commit()

	flash('Brother successfully deleted')

	return list_brothers()

@admin.route('/units')
@login_required
def list_units():
	"""
	List all employees
	"""
	check_admin()

	units = Unit.query.all()
	return render_template('admin/units/units.html',
						   units=units, title='Units', current_user=current_user)

@admin.route('/units/add', methods=['GET', 'POST'])
@login_required
def add_unit():
	check_admin()

	form = UnitForm()
	if form.validate_on_submit():
		unit = Unit(name=form.name.data,
						location=form.location.data)
		try:
			# add item to the database
			db.session.add(unit)
			db.session.commit()
			flash('You have successfully added a new unit.')
		except:
			# in case item name already exists
			flash('Error: item name already exists.', 'danger')

		# redirect to items page
		return redirect(url_for('admin.list_units'))

	# load item template
	return render_template('admin/units/unit.html', action="Add",
						form=form,
						   title="Add Unit")

@admin.route('/units/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_unit(id):
	"""
	Edit a unit
	"""
	check_admin()

	add_unit = False

	unit = Unit.query.get_or_404(id)
	form = UnitForm(obj=unit)
	if form.validate_on_submit():
		unit.name = form.name.data
		unit.location = form.location.data
		db.session.add(unit)
		db.session.commit()
		flash('You have successfully edited the unit.')

		# redirect to the units page
		return redirect(url_for('admin.list_units'))

	return render_template('admin/units/unit.html', action="Edit",
						   add_unit=add_unit, form=form,
						   unit=unit, title="Edit Unit")

@admin.route('/units/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_unit(id):
	"""
	Delete a unit from the database
	"""
	check_admin()

	unit = Unit.query.get_or_404(id)
	db.session.delete(unit)
	db.session.commit()
	flash('You have successfully deleted the Unit.')

	# redirect to the units page
	return redirect(url_for('admin.list_units'))

@admin.route('/units/list_items/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def list_items_unit(unit_id):

	check_admin()

	unit = Unit.query.get_or_404(unit_id)

	return render_template('admin/items/items_in_unit.html', unit=unit, title="Items")

@admin.route('/units/shelves/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def list_shelves(unit_id):

	check_admin()

	unit = Unit.query.filter_by(id=unit_id).first()
	shelves = Shelf.query.filter_by(unit_id=unit_id).all()

	return render_template('admin/shelves/shelves.html',
						   unit=unit, shelves=shelves, title='Shelves')


@admin.route('/units/add_shelf/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def add_shelf(unit_id):
	"""
	Add a shelf to a unit
	"""
	check_admin()

	shelf = Shelf(unit_id=unit_id)
	unit = Unit.query.filter_by(id=unit_id).first()
	form = ShelfContainerForm()
	if form.validate_on_submit():
		shelf.name = form.name.data
		db.session.add(shelf)
		db.session.commit()
		flash('You have successfully added a shelf to the unit.')

		# redirect to the units page
		return redirect(url_for('admin.list_shelves', unit_id=unit_id))

	return render_template('admin/shelves/shelf.html', action="Add",
						   form=form, unit=unit, title="Add Shelf")

@admin.route('/units/edit_shelf/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_shelf(id):
	"""
	Add a shelf to a unit
	"""
	check_admin()

	shelf = Shelf.query.get(id)
	unit = Unit.query.filter_by(id=shelf.unit_id).first()
	form = ShelfContainerForm(obj=shelf)
	if form.validate_on_submit():
		shelf.name = form.name.data
		db.session.add(shelf)
		db.session.commit()
		flash('You have successfully edited the shelf.')

		# redirect to the units page
		return redirect(url_for('admin.list_shelves', unit_id=unit.id))

	return render_template('admin/shelves/shelf.html', action="Edit",
						   form=form, unit=unit, title="Edit Shelf")

@admin.route('/units/delete_shelf/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_shelf(id):
	"""
	Delete a unit from the database
	"""
	check_admin()

	shelf = Shelf.query.get_or_404(id)
	unit_id = shelf.unit_id
	db.session.delete(shelf)
	db.session.commit()

	# redirect to the units page
	return redirect(url_for('admin.list_shelves', unit_id=unit_id))

@admin.route('/containers', methods=['GET', 'POST'])
@admin.route('/containers/<int:shelf_id>', methods=['GET', 'POST'])
@login_required
def list_containers(shelf_id=None):

	check_admin()

	shelf = Shelf.query.filter_by(id=shelf_id).first()
	if shelf_id:
		containers = Container.query.filter_by(shelf_id=shelf_id).all()
	else:
		containers = Container.query.all()

	return render_template('admin/containers/containers.html',
							shelf=shelf, containers=containers, title='Containers')

@admin.route('/containers/add', methods=['GET', 'POST'])
@admin.route('/containers/add/<int:shelf_id>', methods=['GET', 'POST'])
@login_required
def add_container(shelf_id=None):
	"""
	Add a shelf to a unit
	"""
	check_admin()

	container = Container(shelf_id=shelf_id)
	if shelf_id:
		form = ShelfContainerForm()
		shelf = Shelf.query.filter_by(id=shelf_id).first()
		container.unit_id = shelf.unit_id
	else:
		form = ShelfContainerLocationUnknownForm()
		shelf = None

	if form.validate_on_submit():
		container.name = form.name.data
		if not shelf_id:
			container.unit_id = form.unit.data.id
		db.session.add(container)
		db.session.commit()
		flash('You have successfully added a container.')

		# redirect to the units page
		return redirect(url_for('admin.list_containers', shelf_id=shelf_id))

	return render_template('admin/containers/container.html', action="Add",
						   form=form, shelf=shelf, title="Add Container")

@admin.route('/containers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_container(id):
	"""
	Add a shelf to a unit
	"""
	check_admin()

	container = Container.query.get(id)
	shelf = Shelf.query.filter_by(id=container.shelf_id).first()
	form = ShelfContainerForm(obj=container)
	if form.validate_on_submit():
		container.name = form.name.data
		db.session.add(container)
		db.session.commit()
		flash('You have successfully edited the cotainer.')

		# redirect to the units page
		return redirect(url_for('admin.list_containers'))

	return render_template('admin/containers/container.html', action="Edit",
						   form=form, shelf=shelf, title="Edit Shelf")

@admin.route('/containers/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_container(id):
	"""
	Delete a unit from the database
	"""
	check_admin()

	container = Container.query.get_or_404(id)
	db.session.delete(container)
	db.session.commit()

	# redirect to the units page
	return redirect(url_for('admin.list_containers'))

@admin.route('/containers/list_items/<int:container_id>', methods=['GET', 'POST'])
@login_required
def list_items_container(container_id):

	check_admin()

	container = Container.query.get_or_404(container_id)

	return render_template('admin/items/items_in_container.html', container=container, title="Items")


@admin.route('/container/remove_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def remove_item(item_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	item = Item.query.get_or_404(item_id)
	if not item.container:
		flash('Item has no container to remove')
		return redirect(url_for('admin.list_items'))

	item.container_id = None
	try:
		db.session.add(item)
		db.session.commit()
	except:
		flash('Error: Item was not removed.')

	flash('You have successfully removed the item from the container.')
	return redirect(url_for('admin.list_items'))

@admin.route('/containers/assign_unit/<int:container_id>', methods=['GET', 'POST'])
@login_required
def assign_unit_container(container_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	container = Container.query.get_or_404(container_id)

	if len(Unit.query.all()) == 0:
		flash('There are no units.')
		return redirect(url_for('admin.list_containers'))

	form = AssignUnitForm()

	if form.validate_on_submit():
		container.unit_id = form.unit.data.id

		try:
			db.session.add(container)
			db.session.commit()
		except:
			flash('Error: Unit was not assigned')

		flash('You have successfully assigned a unit to the container.')
		return redirect(url_for('admin.list_containers'))

	# redirect to the items page
	return render_template('admin/units/unit.html',
						   object=container, title='Assign Unit', form=form)

@admin.route('/containers/assign_shelf/<int:container_id>', methods=['GET', 'POST'])
@login_required
def assign_shelf_container(container_id):
	"""
	Delete a item from the database
	"""
	check_admin()

	container = Container.query.get_or_404(container_id)

	if container.unit is None:
		flash ('Please assign a Unit to the Item first')
		return redirect(url_for('admin.list_containers'))

	shelves = Shelf.query.filter_by(unit_id=container.unit.id).all()
	if len(shelves) == 0:
		flash('There are no shelves in this unit. Add some shelves!')
		return redirect(url_for('admin.list_containers'))

	shelves_with_no = [(shelf.id,shelf.name) for shelf in shelves]

	form = AssignShelfForm()
	form.shelf.choices = shelves_with_no

	if form.validate_on_submit():
		container.shelf_id = form.shelf.data

		try:
			db.session.add(container)
			db.session.commit()
		except:
			flash('Error: Shelf was not assigned')

		flash('You have successfully assigned a shelf to the container.')
		return redirect(url_for('admin.list_containers', shelf_id=container.shelf_id))

	# redirect to the items page
	return render_template('admin/shelves/shelf.html',
						   object=container, unit=container.unit, title='Assign Shelf', form=form)