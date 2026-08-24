# -*- encoding: utf-8 -*-
"""
Training and testing views
"""
from datetime import datetime

from flask import request, redirect, render_template, url_for
from flask_login import login_required

from logbook.utilities import role_required
from logbook.authentication.models import User
from . import blueprint
from .models import Course, Training, StudentsCourses
from .forms import AddCourseForm, AddTrainingForm


@blueprint.get('/')
@login_required
@role_required('foreman', 'admin')
def index():

    courses = Course.select_all()

    return render_template('training/index.html',
                           courses = courses,
                           segment = "training")

@blueprint.route('/add-course', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_course():

    courseForm = AddCourseForm()

    if courseForm.validate_on_submit():

        newCourse = Course(
            name = courseForm.name.data,
            provider = courseForm.provider.data,
            duration = courseForm.duration.data
        )
        newCourse.save()

        return redirect(url_for('.index'))

    return render_template('training/add-course.html',
                           form = courseForm,
                           segment = "training")

@blueprint.route('/<int:_id>/add-training', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_training(_id):

    course = Course.find_by_id(course=_id)
    concretors = User.query.all()
    trainingForm = AddTrainingForm()
     
    if trainingForm.validate_on_submit():
        newTraining = Training(date = trainingForm.date.data,
                               location = trainingForm.location.data,
                               course_id = _id
        )
        # association object, uni-directional
        learners = User.select_learners(request.form.getlist("students"))
        for learner in learners:
            # make association before relationship is formed
            nta = StudentsCourses(student_id=learner.id, training_id=newTraining.id)
            nta.learner = learner
            newTraining.students.append(nta)

        newTraining.save()
        
        return redirect(url_for('.index'))

    return render_template('training/add-training.html',
                           form = trainingForm,
                           course = course,
                           learners = [(concretor.id, concretor.username) for concretor in concretors],
                           segment = "training")
    
@blueprint.get('/<int:courseid>')
@login_required
@role_required('foreman', 'admin')
def view_training(courseid):

    course = Course.find_by_id(courseid)
    events = Training.find_by_course(courseid)

    return render_template('training/view-training.html',
                           segment="training",
                           course=course,
                           training=events,
                           datetimenow = datetime.now())

@blueprint.post('/<string:slug>/<int:trainingid>/mark')
@login_required
@role_required('admin')
def mark_training(slug, trainingid):

    event = Training.find_by_id(trainingid)
    scDetails = []
    for student in event.students:
        scDetails.append({"training_id": trainingid, "student_id": student.student_id, "is_complete": True})
    StudentsCourses.complete_training(scDetails)
    print(slug)

    return redirect(url_for('.view_training', courseid=event.course_id))

import re
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

@blueprint.app_template_filter('slugify')
def slugify(value):
    '''Normalizes string, converts to lowercase and spaces to hyphens.'''    
    if not isinstance(value, str):
        value = str(value)
    #import unicodedata
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = _slugify_strip_re.sub('', value).strip().lower()

    return _slugify_hyphenate_re.sub('-', value)

