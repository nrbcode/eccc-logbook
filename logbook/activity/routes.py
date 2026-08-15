# -*- encoding: utf-8 -*-
"""
Logbook Activity
"""
from datetime import datetime

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import current_user, login_required

from . import blueprint
from .forms import LogbookForm, EditProfileForm
from .models import LogEntry

# import logbook
from logbook.constants import CONTROL_MEASURES
from logbook.utilities import get_segment, role_required
from logbook.authentication.models import User
from logbook.training.models import Training

#******************************************************************************
# GUI views

@blueprint.get('/my-logbook')
@login_required
def my_logbook():

    """    Table of logbook entries.    """
    page_num = request.args.get('page', 1, type=int)
    entries = LogEntry.find_by_concretor(_id=current_user.id).paginate(
        page=page_num, per_page=5, error_out=False)
    
    return render_template('logbook/index.html',
                           entries=entries,
                           segment=get_segment(request),
                           page=page_num,
                           per_page=5
                           )

@blueprint.route('/my-logbook/new', methods=["GET", "POST"])
@login_required
def new_logbook_entry():
    """    Record new safety checklist.   """
    
    logbook_entry = LogbookForm(request.form)
    logbook_entry.controls_list.choices = CONTROL_MEASURES
    
    if logbook_entry.validate_on_submit():

        newentry = {
            "site": logbook_entry.job_site.data,
            "date": logbook_entry.job_date.data,
            "activity": logbook_entry.job_task.data,
            "duration": float(request.form.get("job_duration")),
            "controls": '; '.join(logbook_entry.controls_list.data),
            "concretor_id": current_user.id
            }
        
        logentry = LogEntry(**newentry)
        logentry.save()

        return redirect(url_for('.my_logbook'))
    
    return render_template('logbook/new-entry.html',
                           segment = 'logbook',
                           datetimenow = datetime.now(),
                           form = logbook_entry)

@blueprint.get('/my-profile')
@login_required
def my_profile():
    
    courses = Training.query.all()
    return render_template('logbook/my-profile.html',
                           segment = get_segment(request),
                           training = courses
                           )

@blueprint.route('/my-profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_profile = EditProfileForm(request.form)
    
    # Locate user
    user = User.find_by_username(username=current_user.username)

    if edit_profile.validate_on_submit():
        user_details = {
            "firstname": edit_profile.firstname.data,
            "lastname": edit_profile.lastname.data,
            "address": edit_profile.address.data,
            "bio": edit_profile.bio.data
        }
        user.update_user(user_details)

        return redirect(url_for('.my_profile'))

    return render_template( 'logbook/edit-profile.html',
                          form=edit_profile, 
                          segment='profile')

#******************************************************************************
# Errors

@blueprint.errorhandler(403)
def access_forbidden(error):
    print(error)
    return render_template('home/page-403.html'), 403

#******************************************************************************
# Admin views

@blueprint.get('/all-logbook')
@login_required
@role_required('foreman', 'admin')
def view_logbook():

    """    Table of pre-start records.    """
    page_num = request.args.get('page', 1, type=int)
    show = 10
    entries = LogEntry.query.paginate(page=page_num, per_page=show, error_out=False)

    return render_template(
        'logbook/index.html',
        segment = 'query',
        entries = entries,
        admin = True,
        page = page_num,
        per_page = show
    )

@blueprint.get('/all-concretors')
@login_required
def all_concretors():

    page_num = request.args.get('page', 1, type=int)
    show = 5    
    concretors = User.query.paginate(page=page_num, per_page=show, error_out=False)

    return render_template('logbook/concretors.html',
                           admin = True,
                           title = "All Concretors",
                           subtitle = "All registered concretors.",
                           entries = concretors,
                           segment = 'query',
                           page = page_num,
                           per_page = show
    )


#******************************************************************************
# API

@blueprint.get('/user_info')
@login_required
def user_info():

    if current_user.is_authenticated:
        resp = {"result": 200,
                "data": current_user.to_json()}
    else:
        resp = {"result": 401,
                "data": {"message": "user no login"}}
    return jsonify(**resp)
 