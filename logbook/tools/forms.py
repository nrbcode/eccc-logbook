# -*- encoding: utf-8 -*-
"""
Tool Registration and Tagging Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField
from wtforms.fields import RadioField, SelectField
from wtforms.validators import InputRequired, DataRequired #, Optional, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

from logbook.constants import POWER_TOOLS, TOOL_TYPES


class AddNewTool(FlaskForm):
    brand_name = StringField("Brand", validators=[InputRequired()])
    model_number = StringField("Model", validators=[InputRequired()])
    tool_name = SelectField("Tool Name", choices=POWER_TOOLS, validators=[DataRequired()])
    tool_type = RadioField("Tool Type", choices=TOOL_TYPES, validators=[DataRequired()])
    serial_num = StringField("Serial Number")
    notes = TextAreaField("Extra notes")
    submit = SubmitField('Register New Tool')

# upload profile image
class UploadImageForm(FlaskForm):

    upload = FileField('Update tool picture', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Upload Image')

class ToolTagForm(FlaskForm):
    
    tag_date  = DateField("Date on Tag", validators=[DataRequired()])
    tag_num = StringField("Tag Number")
    next_test = DateField("Next Test Due", validators=[DataRequired()])
    submit = SubmitField("Tag Corded Tool")