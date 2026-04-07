# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from wsgiref.validate import validator
from flask_wtf import FlaskForm
#from wtforms.fields.simple import SubmitField
from wtforms import StringField, DateField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired
#from wtforms.fields import SelectField


class LogbookForm(FlaskForm):
    """ """    
    job_site = StringField("Site", validators=[InputRequired()])
    job_date = DateField("Date of Job", validators=[DataRequired()])
    job = TextAreaField("Work Activity", validators=[InputRequired()])
    submit_entry = SubmitField('Submit')

    #checklist = FieldList(StringField("Controls"))
    #created_at = DateField("Date", format='%d-%m-%Y', validators=[DataRequired()])
    

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

    

