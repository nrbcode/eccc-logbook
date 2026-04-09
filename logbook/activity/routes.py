# -*- encoding: utf-8 -*-
""" logbook/activity/ """

import json
from datetime import datetime
from flask import render_template, redirect, request, url_for, jsonify
from flask_login import current_user, login_required
#from jinja2 import TemplateNotFound

from . import blueprint
from .constants import CONTROL_MEASURES
from .forms import LogbookForm, EditProfileForm
from .models import LogEntry

from logbook.authentication.models import User


CONTROLS = dict(enumerate(CONTROL_MEASURES, start=1))

#******************************************************************************

#******************************************************************************

@blueprint.route('/user_info', methods=['GET'])
@login_required
def user_info():

    if current_user.is_authenticated:
        resp = {"result": 200,
                "data": current_user.to_json()}
    else:
        resp = {"result": 401,
                "data": {"message": "user no login"}}
    return jsonify(**resp)

@blueprint.route('/all_users', methods=['GET'])
@login_required
def all_users():
    result = User.find_all()
    json_str = json.dumps([ob.username for ob in result])
    resp = {"result": 200,
            "data": json_str}

    return jsonify(**resp)

@blueprint.get('/all-logbook')
@login_required
def view_logbook():

    """    Table of pre-start records.    """
    page_num = request.args.get('page', 1, type=int)
    #entries = LogEntry.query.all()
    entries = LogEntry.query.paginate(page=page_num, per_page=10, error_out=False)

    # Detect the current page
    segment = get_segment(request)
    
    return render_template(
        'logbook/index.html',
        segment=segment,
        entries=entries,
        admin=True,
        page=page_num,
        per_page=10
    )

@blueprint.route('/all-concretors', methods=['GET'])
@login_required
def all_concretors():
    """
    result = User.find_all()
    json_str = json.dumps([ob.username for ob in result])
    resp = {"result": 200,
            "data": json_str}

    return jsonify(**resp)"""
    users = User.query.all()
    return render_template('logbook/concretors.html', concretors=users)

#******************************************************************************

#******************************************************************************

@blueprint.get('/my-logbook')
@login_required
def my_logbook():

    """    Table of logbook entries.    """
    page_num = request.args.get('page', 1, type=int)
    entries = LogEntry.find_by_concretor(_id=current_user.id).paginate(
        page=page_num, per_page=5, error_out=False)
    segment = get_segment(request)

    return render_template( 'logbook/index.html',
                           entries=entries,
                           segment=segment,
                           page=page_num,
                           per_page=5
                           )

@blueprint.route('/my-logbook/new', methods=["GET", "POST"])
@login_required
def new_logbook_entry():
    """    Record new safety checklist.   """
    
    logbook_entry = LogbookForm(request.form)
    
    if logbook_entry.validate_on_submit():

        # convert list integers to strings
        cl = request.form.getlist("cl")
        controls = [CONTROLS[int(num)] for num in cl]
        
        #logbook_entry.populate_obj(newentry) 
        newentry = {
            "site": logbook_entry.job_site.data,
            "date": logbook_entry.job_date.data,
            "activity": logbook_entry.job_task.data,
            "duration": float(request.form.get("job_duration")),
            "controls": json.dumps(controls),
            "concretor_id": current_user.id
            }
        
        logentry = LogEntry(**newentry)
        logentry.save()

        return redirect(url_for('.my_logbook'))
    
    return render_template( 'logbook/new-entry.html',
                           checklist = enumerate(CONTROL_MEASURES, start=1),
                           segment = 'logbook',
                           datetimenow = datetime.now(),
                           form = logbook_entry)

@blueprint.get('/my-profile')
@login_required
def my_profile():
    
    return render_template( 'logbook/my-profile.html', segment='profile')

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


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
 