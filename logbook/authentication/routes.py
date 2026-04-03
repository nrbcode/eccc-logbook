# -*- encoding: utf-8 -*-
""" logbook/authentication/routes """

from flask import render_template, redirect, request, url_for

from flask_login import current_user, login_user, logout_user

from logbook import bc, db, login_manager
from logbook.authentication import blueprint
from logbook.authentication.forms import LoginForm, CreateAccountForm
from logbook.authentication.models import User


# Callbacks
@login_manager.user_loader
def load_user(user_id):

    return User.query.filter_by(id=user_id).first()
    
# request (API) callback
@login_manager.request_loader
def request_loader(request):
    name = request.args.get('username')
    user = User.find_by_username(username=name)
    
    return user if user else None


# Views
@blueprint.route('/')
def route_default():
    if current_user.is_authenticated:
        return redirect(url_for('activity_blueprint.my_logbook'))
    else:
        return redirect(url_for('.login'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    login_form = LoginForm(request.form)

    if login_form.validate_on_submit():

        print('user validated!')

        # read form data
        u = login_form.username.data
        p = login_form.password.data

        # Locate user
        user = db.session.scalar(db.select(User).filter_by(username=u))

        # if user not found
        if not user:
            return render_template( 'accounts/login.html',
                                   msg='Unknown User or Email',
                                   form=login_form)

        # Check the password
        ph = db.session.scalar(db.select(User.pw_hash).where(User.username == u))
        if bc.check_password_hash(ph, p):
        
            login_user(user)
            print("user logged in!")
            return redirect(url_for('activity_blueprint.my_logbook'))

        # Something (user or pass) is not ok
        print("user NOT logged in!")
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    #return render_template('accounts/login.html', form=login_form)
    return render_template('home/landing.html', form=login_form)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    
    if create_account_form.validate_on_submit():
        print('registration validated!')

        u = create_account_form.username.data
        e = create_account_form.email.data
        p = create_account_form.password.data

        # Check username exists
        user = db.session.scalar(db.select(User).where(User.username == u))
        if user is not None:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = db.session.scalar(db.select(User).where(User.email == e))
        if user is not None:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        ph = bc.generate_password_hash(p).decode('utf-8')
        #user = Users(**request.form)
        #create_account_form.populate_obj(user) 
        user = User(username=u, email=e, pw_hash=ph)
        user.save()
        
        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               form=create_account_form,
                               success=True
                               )
    else:
        print('form not validated!')
        return render_template('accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
