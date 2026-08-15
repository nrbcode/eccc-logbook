# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present softpowerware
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import InputRequired, DataRequired
from wtforms.fields import RadioField


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, displaying a list of checkboxes.
    """
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class LogbookForm(FlaskForm):
    """ """    
    job_site = StringField("Job Site", validators=[InputRequired()])# jinja macro
    job_date = DateField("Date of Job", validators=[DataRequired()])
    job_task = RadioField("Work Activity",
                         choices=[('floor grinder', 'Walk-behind Grinder'), ('hand grinder', 'Hand Grinder'), ('jackhammer', 'Jackhammer'), ('drill', 'Drill into Concrete')],
                         validators=[InputRequired()])
    controls_list = MultiCheckboxField("Control Measures Used")
    submit_entry = SubmitField('Submit')

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
