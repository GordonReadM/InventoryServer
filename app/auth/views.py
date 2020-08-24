from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from . import auth
from .forms import RegistrationForm, LoginForm, ReservationAddForm, ReservationAddForItemForm, ReservationEditForm, ResetPasswordGetEmailForm, ResetPasswordForm
from .. import db, mail
from ..models import Item, Reservation, Brother, Unit, Shelf, Container
from ..security import generate_confirmation_token, confirm_token


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an employee to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        brother = Brother(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data,
                            is_admin=False,
                            email_confirmed=False)

        # add employee to the database
        db.session.add(brother)
        db.session.commit()

        token = generate_confirmation_token(brother.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('auth/activate.html', confirm_url=confirm_url)

        toFlash = 'A confirmation email has been sent to the address you provided, please confirm before continuing'

        msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Please Confirm Your Email', recipients=[brother.email])
        mail.send(msg)

        flash(toFlash)
        # redirect to the dashboard page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        brother = Brother.query.filter_by(email=form.email.data).first()
        if brother is not None and brother.verify_password(form.password.data):
            if not brother.email_confirmed:
            	flash('Unable to login until email is confirmed.')
            	return render_template('auth/login.html', form=form, title='Login')

            # log employee in
            login_user(brother)

            # redirect to the dashboard page after login
            if brother.is_admin:
                return redirect(url_for('home.admin_dashboard'))
            else:
                return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/send_reset_email', methods=['GET', 'POST'])
def send_reset_email():
    form = ResetPasswordGetEmailForm()
    if form.validate_on_submit():
        brother = Brother.query.filter_by(email=form.email.data).first()
        if brother is None:
            flash('Unknown Email')
            return redirect(url_for('auth.login'))

        token = generate_confirmation_token(brother.email)
        confirm_url = url_for('auth.reset_password', token=token, _external=True)
        html = render_template('auth/reset_email.html', confirm_url=confirm_url)

        toFlash = 'A link to reset has been sent to the address you provided'

        msg = Message(html=html, sender='alphagammawebmaster@gmail.com', subject='Reset Password Link', recipients=[brother.email])
        mail.send(msg)

        flash(toFlash)

        return redirect(url_for('auth.login'))

    return render_template('auth/reset.html', form=form, title='Reset Password')


@auth.route('/get_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_token(token, expiration=1800)
        brother = Brother.query.filter_by(email=email).first()
        if brother is None:
            raise AttributeError('Invalid Email Encoding')
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        brother.password = form.new_password.data
        db.session.add(brother)
        db.session.commit()
        flash('You have successfully reset your password!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset.html', form=form, title='Reset Password')



@auth.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    brother = Brother.query.filter_by(email=email).first()
    if brother is None:
        flash('Invalid Link.')
        return redirect(url_for('auth.login'))

    if brother.email_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        brother.email_confirmed = True
        db.session.add(brother)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    if brother.is_admin:
        return redirect(url_for('home.admin_dashboard'))
    else:
        return redirect(url_for('home.dashboard'))

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))

@auth.route('/items', methods=['GET', 'POST'])
@auth.route('/items/<int:type_code>/<int:object_id>', methods=['GET', 'POST'])
@login_required
def list_items(type_code=-1, object_id=None):
    """
    List all items
    """

    shelf = Shelf()
    unit = Unit()
    if type_code == -1:
        items = Item.query.all()
        for item in items:
            if item.unit_id:
                item.unit = Unit.query.filter_by(id=item.unit_id).first()
            else:
                item.unit = None
            if item.shelf_id:
                item.shelf = Shelf.query.filter_by(id=item.shelf_id).first()
            else:
                item.shelf = None
    elif type_code == 0:
        items = Item.query.filter_by(shelf_id=object_id).all()
        shelf = Shelf.query.get(object_id)
        unit = Unit.query.filter_by(id=shelf.unit_id).first()
    elif type_code == 1:
        #item_id is 0 and brother_id is not
        items = Item.query.filter_by(unit_id=object_id).all()
        unit = Unit.query.get(object_id)

    return render_template('auth/items/items.html',
                           items=items, unit=unit, shelf=shelf,
                           title="Items")

@auth.route('/reservations')
@auth.route('/reservations/<int:type_code>/<int:object_id>')
@login_required
def list_reservations(type_code=-1, object_id=0):
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

    return render_template('auth/reservations/reservations.html',
                           reservations=reservations, title='Reservations', item=item, brother=brother)

@auth.route('/reservations/add', methods=['GET', 'POST'])
@auth.route('/reservations/add/<int:item_id>', methods=['GET', 'POST'])
@login_required
def add_reservation(item_id=0):
    """
    Add a reservation to the database
    """

    add_reservation = True

    if item_id == 0:
        form = ReservationAddForm()
    else:
        form = ReservationAddForItemForm()
        form.item = Item.query.filter_by(id=item_id).first()

    if form.validate_on_submit():
        # #item = Item.query.filter_by(name=form.item.data).first()
        # if item is None:
        #     flash('Error: requested item does not exist')

        if item_id == 0:
            item_name=form.item.data.name
            item_id=form.item.data.id
        else:
            item_name=form.item.name
            item_id=form.item.id

        reservation = Reservation(reason=form.reason.data,
                    fromDate=form.fromDate.data,
                    toDate=form.toDate.data,
                    item_name = item_name,
                    item_id = item_id,
                    reserved_by=current_user.first_name + ' ' + current_user.last_name,
                    brother_id=current_user.id)

        try:
            # add reservation to the database
            db.session.add(reservation)
            db.session.commit()
            flash('You have successfully added a new reservation for the %s.' % item_name)
        except:
            # in case reservation name already exists
            flash('Error: reservation name already exists.')

        # redirect to the reservations page
        return redirect(url_for('auth.list_reservations'))

    # load reservation template
    return render_template('auth/reservations/reservation.html', add_reservation=add_reservation,
                           form=form, title='Add Reservation')

@auth.route('/reservations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(id):
    """
    Edit a reservation
    """

    add_reservation = False

    reservation = Reservation.query.get_or_404(id)
    form = ReservationEditForm(obj=reservation)
    form.item = reservation.item
    if form.validate_on_submit():
        reservation.reason = form.reason.data
        reservation.fromDate = form.fromDate.data
        reservation.toDate = form.toDate.data
        reservation.approved = False
        db.session.add(reservation)
        db.session.commit()
        flash('You have successfully edited the reservation. It will need to be reapproved.')

        # redirect to the reservations page
        return redirect(url_for('auth.list_reservations'))

    form.reason.data = reservation.reason
    form.fromDate.data = reservation.fromDate
    form.toDate.data = reservation.toDate
    return render_template('auth/reservations/reservation.html', add_reservation=add_reservation,
                           form=form, title="Edit Reservation", item=Item.query.filter_by(id=id).first())

@auth.route('/reservations/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_reservation(id):
    """
    Delete a reservation from the database
    """

    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    flash('You have successfully deleted the reservation.')

    # redirect to the reservations page
    return redirect(url_for('auth.list_reservations'))

    return render_template(title="Delete Reservation")

@auth.route('/brothers')
@login_required
def list_brothers():
    """
    List all employees
    """

    brothers = Brother.query.all()
    return render_template('auth/brothers/brothers.html',
                           brothers=brothers, title='Brothers')

@auth.route('/units')
@login_required
def list_units():
    """
    List all employees
    """

    units = Unit.query.all()
    return render_template('auth/units/units.html',
                           units=units, title='Units')

@auth.route('/units/list_items/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def list_items_unit(unit_id):

    unit = Unit.query.get_or_404(unit_id)

    return render_template('auth/items/items_in_unit.html', unit=unit, title="Items")

@auth.route('/units/shelves/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def list_shelves(unit_id):

    unit = Unit.query.filter_by(id=unit_id).first()
    shelves = Shelf.query.filter_by(unit_id=unit_id).all()
    
    return render_template('auth/shelves/shelves.html',
                           unit=unit, shelves=shelves, title='Shelves')

@auth.route('/containers', methods=['GET', 'POST'])
@auth.route('/containers/<int:shelf_id>', methods=['GET', 'POST'])
@login_required
def list_containers(shelf_id=None):


    shelf = Shelf.query.filter_by(id=shelf_id).first()
    if shelf_id:
        containers = Container.query.filter_by(shelf_id=shelf_id).all()
    else:
        containers = Container.query.all()

    return render_template('auth/containers/containers.html',
                            shelf=shelf, containers=containers, title='Containers')
    
@auth.route('/containers/list_items/<int:container_id>', methods=['GET', 'POST'])
@login_required
def list_items_container(container_id):

    container = Container.query.get_or_404(container_id)

    return render_template('auth/items/items_in_container.html', container=container, title="Items")
