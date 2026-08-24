# -*- encoding: utf-8 -*-
"""
Training Enrolment Forms
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import InputRequired, DataRequired


class AddCourseForm(FlaskForm):

    name = StringField("Course Name", validators=[InputRequired()])
    provider = StringField("Provider Name", validators=[InputRequired()])
    duration = IntegerField("Duration (Number of Days)", validators=[DataRequired()])
    submit = SubmitField("Create New Training Course")


class AddTrainingForm(FlaskForm):

    date  = DateField("Date of Training", validators=[DataRequired()])
    location = StringField("Location of Training", validators=[InputRequired()])
    submit = SubmitField("Create New Training Event")
