# -*- encoding: utf-8 -*-
"""
Training Enrolment Forms
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField, FieldList, FormField
from wtforms.validators import InputRequired, DataRequired


class AddCourseForm(FlaskForm):

    name = StringField("Course Name", validators=[InputRequired()])
    provider = StringField("Provider Name", validators=[InputRequired()])
    duration = IntegerField("Duration (Number of Days)", validators=[DataRequired()])
    submit = SubmitField("Submit New Training Course")


class StudentForm(FlaskForm):
    cid = IntegerField("Concretor id", validators=[DataRequired()])
    cname = StringField("Concretor name", validators=[DataRequired()])


class AddTrainingForm(FlaskForm):

    date  = DateField("Date of Training", validators=[DataRequired()])
    location = StringField("Location of Training", validators=[InputRequired()])
    students = FieldList(FormField(StudentForm))
    submit = SubmitField("Submit New Training Event")
