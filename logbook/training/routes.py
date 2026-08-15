# -*- encoding: utf-8 -*-
"""
Training and testing views
"""

#from random import choices

from flask import request, redirect, render_template, url_for
from flask_login import login_required

from logbook.utilities import get_segment
from logbook.authentication.models import User
from . import blueprint
from .models import Course, Training, StudentsCourses
from .forms import AddCourseForm, AddTrainingForm


@blueprint.get('/')
@login_required
def index():

    courses = Course.select_all()
    #segment = get_segment(request)

    return render_template('training/index.html',
                           courses = courses,
                           segment = "training")

@blueprint.route('/add-course', methods=['GET', 'POST'])
def add_course():

    courseForm = AddCourseForm()

    if courseForm.validate_on_submit():
        print("Success! Form submitted.")

        newCourse = Course(
            name = courseForm.name.data,
            provider = courseForm.provider.data,
            duration = courseForm.duration.data
        )
        newCourse.save()

        return redirect(url_for('.index'))

    else:
       print("Course form not submitted!")

    return render_template('training/add-course.html',
                           form = courseForm,
                           segment = "training")

@blueprint.route('/<string:_id>/add-training', methods=['GET', 'POST'])
def add_training(_id):

    course = Course.query.filter_by(id=_id).first()
    concretors = User.query.all()
    trainingForm = AddTrainingForm()
     
    if trainingForm.validate_on_submit():
        print("Success! Form submitted.")
        
        # each training event is a new course
        newTraining = Training.event(
            course_obj = course,
            date = trainingForm.date.data,
            location = trainingForm.location.data
        )
        # association object, uni-directional
        learners = User.select_learners(request.form.getlist("students"))
        for learner in learners:
            # make association before relationship is formed
            nta = StudentsCourses(student_id=learner.id, training_id=newTraining.training_id)
            nta.learner = learner
            newTraining.students.append(nta)

        newTraining.save()
        
        return redirect(url_for('.index'))
    else:
        print("Training form not submitted!")

    return render_template('training/add-training.html',
                           form = trainingForm,
                           course = course,
                           learners = [(concretor.id, concretor.username) for concretor in concretors],
                           segment = "training")
    
@blueprint.get('/<string:name>/view-training')
def view_training(name):

    events = Training.find_by_coursename(name)

    return render_template('training/view-training.html',
                           training=events,
                           coursename = name,
                           segment = "training")



