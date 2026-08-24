# -*- encoding: utf-8 -*-
"""
Course Register and Student Training Journal
"""

from typing import List

from sqlalchemy import func, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from logbook import db


class Course(db.Model):
    '''Record each training course.'''
    __tablename__ = 'training_courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    provider = db.Column(db.String(64))
    duration = db.Column(db.Integer, nullable=False)
    
    def __init__(self, name, provider, duration):
        self.name = name
        self.provider = provider
        self.duration = duration

    def __str__(self):
        return f'{self.name}, {self.provider}'
    
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
    def select_all(cls) -> List["Course"]:
        '''Retieve all courses.'''
        #return db.session.scalars(db.select(cls).group_by("name")) # SQLite
        return db.session.scalars(db.select(cls).distinct("name")) # POSTGRESQL

    @classmethod
    def find_by_id(cls, course: int) -> "Course":
        '''Select one course.'''
        return db.session.scalar(db.select(cls).filter_by(id=course))


class StudentsCourses(db.Model):
    '''Association Object: association table with extra data.'''
    __tablename__ = "students_courses"

    # Associations
    training_id = db.Column("course_id", db.ForeignKey("training_events.id"), primary_key=True)
    student_id = db.Column("student_id", db.ForeignKey("logbook_users.id"), primary_key=True)
    
    # Extra data
    is_complete = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    
    # uni-directional, many training events to one learner
    learner = db.relationship("User")
    
    @classmethod
    def complete_training(cls, completion_details):
        '''Update completion state following attendance.'''
        db.session.execute(update(cls), completion_details)
        db.session.commit()


class Training(db.Model):
    '''Record each training event.'''
    __tablename__ = 'training_events'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    location = db.Column(db.String(64))
    course_id = db.Column(db.Integer, db.ForeignKey("training_courses.id"))    
    
    students = db.relationship("StudentsCourses")# uni-directional, one training event to many students
    
    def __init__(self, date, location, course_id):
        self.date = date
        self.location = location
        self.course_id = course_id

    def __str__(self):
        return f'{self.date}, {self.location}, {self.course_id}'

    @classmethod
    def find_by_course(cls, course: int) -> List["Training"]:
        '''Select all training for one course.'''
        return db.session.scalars(db.select(cls).filter_by(course_id=course))

    @classmethod
    def find_by_id(cls, _id: int) -> "Training":
        '''Select training event.'''
        return db.session.scalar(db.select(cls).filter_by(id=_id))

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
    