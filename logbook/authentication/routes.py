# -*- encoding: utf-8 -*-
"""
Authentication
"""
import json
import logging

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message

from logbook import bc, lm, fm
from . import blueprint
from .forms import LoginForm, CreateAccountForm, ResetPasswordLink, ResetPasswordForm
from .models import User

#******************************************************************************
# GUI views

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

        # read form data
        u = login_form.username.data
        p = login_form.password.data

        # Locate user
        user = User.find_by_username(u)
        if not user:

            # unknown user
            msg = "Unknown username"

        elif user.verified:

            # Check the password
            if bc.check_password_hash(user.pw_hash, p):
                login_user(user)

                return redirect(url_for('activity_blueprint.my_logbook'))
            else:
                msg = "Wrong password"
        else:
            msg = "Email not yet verified"

        # Something (user or pass or verified) is not ok
        return render_template('home/landing.html',
                               msg=msg,
                               form=login_form)

    return render_template('home/landing.html', form=login_form)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    
    if create_account_form.validate_on_submit():
        
        u = create_account_form.username.data
        e = create_account_form.email.data
        p = create_account_form.password.data

        # Check username exists
        user = User.find_by_username(u)
        if user is not None:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form
                                   )
        # Check email exists
        user = User.find_by_email(e)
        if user is not None:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form
                                   )

        # Create new account
        ph = bc.generate_password_hash(p).decode('utf-8')
        user = User(username=u, email=e, pw_hash=ph)
        user.save()
        
        # Generate message for email verification
        token = user.generate_confirmation_token()
        verify_url = url_for('.verify_email', token=token, _external=True)
        send_verification_email(user.username, "Verify Email", user.email, verify_url)
        
        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg="Account registered. Please check your email for verification link.",
                               form=create_account_form,
                               success=True
                               )

    return render_template('accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.login')) 

@blueprint.route('/reset-password', methods=['GET', 'POST'])
def reset_password_link():
    """
    Send JWT to email.
    Email address must be registered and verified.
    """
    if current_user.is_authenticated:

        return redirect(url_for('activity_blueprint.my_logbook'))
    reset_password_form = ResetPasswordLink(request.form)
    msg = None
    success = False

    if reset_password_form.validate_on_submit():

        e = reset_password_form.email.data

        # Check email exists
        user = User.find_by_email(e)

        if user:
            # Generate message for email verification
            token = user.generate_confirmation_token()
            verify_url = url_for('.reset_password', token=token, _external=True)
            send_verification_email(user.username, "Reset Password", user.email, verify_url)
            
            msg = "Please check Email for Reset Password link"
            success = True

        if user is None:
            msg='Email not registered'
            
    return render_template('accounts/send-reset-link.html',
                          msg=msg,
                          success=success,
                          form=reset_password_form
                          )

@blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Show the reset password page only when valid JWT is provided.
    """
    if current_user.is_authenticated:

        return redirect(url_for('activity_blueprint.my_logbook'))
    user = User.confirm_token(token)

    if not user:

        return redirect(url_for('.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        p = form.password.data
        ph = bc.generate_password_hash(p).decode('utf-8')
        user.update_user({'pw_hash': ph})
        logout_user()
        logging.info("Password reset by verified email!")

        return redirect(url_for('.login'))

    return render_template('accounts/reset-password.html', form=form)

@blueprint.route('/verify/<token>')
def verify_email(token):
    """
    JWT to verify user email account.
    """
    user = User.confirm_token(token)
    if not user:
        return "Invalid or expired verification link."
    elif user.verified:
        return "Account already verified."
    else:
        user.update_user({'verified': True})
        logout_user()
        logging.info("Account has been verified!")

        return redirect(url_for('.login'))

#******************************************************************************
# Callbacks
@lm.user_loader
def load_user(user_id):

    return User.query.filter_by(id=user_id).first()
    
# request (API) callback
@lm.request_loader
def request_loader(request):
    name = request.args.get('username')
    user = User.find_by_username(username=name)
    
    return user if user else None

#******************************************************************************
# Errors
@lm.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    logging.error(f"403 Error: {str(error)}")

    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    logging.error(f"404 Error: {str(error)}")

    return render_template('home/page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    logging.error(f"500 Error: {str(error)}")

    return render_template('home/page-500.html'), 500

#******************************************************************************
# API views

@blueprint.get('/all_users')
@login_required
def all_users():
    result = User.find_all()
    json_str = json.dumps([ob.username for ob in result])
    resp = {"result": 200,
            "data": json_str}

    return jsonify(**resp)

#******************************************************************************
# Helpers

def send_verification_email(name, subject, to, verify_url):
    """Send the verification email with a secure link."""
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html = render_template('email/verify-email.html',
                                   name=name,
                                   verify_url=verify_url,
                                   subject=subject)
        )
        fm.send(msg)
        logging.info(f"Verification email sent to {to}.")
    except Exception as e:
        logging.error(f"Error sending email to {to}: {str(e)}")
