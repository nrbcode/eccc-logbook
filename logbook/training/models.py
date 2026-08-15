# -*- encoding: utf-8 -*-
"""
Course Register and Student Training Journal
"""

from typing import List

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from logbook import db


class Course(db.Model):

    __tablename__ = 'training_courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    provider = db.Column(db.String(64))
    duration = db.Column(db.Integer, nullable=False)
    
    def __init__(self, name, provider, duration):
        self.name = name
        self.provider = provider
        self.duration = duration

    def to_json(self):
        return {
            "course id": self.id,
            "course name": self.name,
            "training provider": self.provider
        }
    
    def __repr__(self):
        return str(self.name)
    
    def save(self) -> None:
        try:
            # Perform database operations
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()  # Crucial to undo failed states
            print(f"Data validation or constraint failed: {e}")
        except SQLAlchemyError as e:
            db.session.rollback()  # Protect transaction integrity
            print(f"A general SQLAlchemy error occurred: {e}")
        else:
            print("Database operation completed successfully.")
        finally:
            db.session.close()  # Clean up and release the connection resource

    
    @classmethod
    def select_all(cls):

        '''Retieve all courses.'''
        #return db.session.scalars(db.select(cls).group_by("id", "name"))
        return db.session.scalars(db.select(cls).distinct("name"))


class StudentsCourses(db.Model):

    '''Association Object: association table with extra data.'''
    __tablename__ = "students_courses"

    student_id = db.Column("student_id", db.ForeignKey("logbook_users.id"), primary_key=True)
    training_id = db.Column("course_id", db.ForeignKey("training_events.training_id"), primary_key=True)
    is_complete = db.Column(db.Boolean, default=False) # extra data 

    # uni-directional
    learner = db.relationship("User")# many training events to one student
        

class Training(Course):

    __tablename__ = 'training_events'

    training_id = db.Column(db.Integer, primary_key=True)###
    date = db.Column(db.Date)
    location = db.Column(db.String(64))
    course_id = db.Column(db.Integer, db.ForeignKey("training_courses.id"))    
    
    students = db.relationship("StudentsCourses")# uni-directional, one training event to many students
    
    def __init__(self, course_id, name, provider, duration, date, location):

        super().__init__(name, provider, duration)
        self.date = date
        self.location = location
        self.course_id = course_id

    def __repr__(self):
        return f'Training({self.training_id}, {self.date}, {self.location})'
    
    def __str__(self):
        return f'{self.name}, {self.location}, {self.date}'

    @classmethod
    def event(cls, course_obj, date, location):

        '''Create training event on existing course.'''
        return cls(course_obj.id, course_obj.name, course_obj.provider, course_obj.duration, date, location)

    def to_json(self):

        return {
            "training id": self.training_id,
            "course name": self.name,
            "training provider": self.provider,
            "training date": self.date,
            "training location": self.location,
            "course id": self.course_id
        }
    
    @classmethod
    def find_by_coursename(cls, course: str) -> List["Training"]:

        '''Select one course.'''
        return db.session.scalars(db.select(cls).filter_by(name=course))
