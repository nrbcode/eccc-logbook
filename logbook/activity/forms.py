# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired
from wtforms.fields import RadioField


class LogbookForm(FlaskForm):
    """ """    
    job_site = StringField("Job Site", validators=[InputRequired()])# jinja macro
    job_date = DateField("Date of Job", validators=[DataRequired()])
    job_task = RadioField("Work Activity",
                         choices=[('floor grinder', 'Walk-behind Grinder'), ('hand grinder', 'Hand Grinder'), ('jackhammer', 'Jackhammer'), ('drill', 'Drill into Concrete')],
                         validators=[InputRequired()])
    submit_entry = SubmitField('Submit')
    #checklist = FieldList(StringField("Controls"))
    

class EditProfileForm(FlaskForm):
    firstname = StringField('FirstName',
                            id='edit_username')
    lastname = StringField('Lastname',
                           id='edit_lastname')
    address = StringField('Address',
                          id='edit_address')
    bio = TextAreaField('Aboutprofile',
                        id='edit_bio',
                        validators=[DataRequired()])

    

