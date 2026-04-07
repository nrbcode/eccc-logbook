# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from ast import List
import json
from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.orm.attributes import set_attribute

from logbook import db


class LogEntry(db.Model, UserMixin):
    '''
    The entire logbook, made up of entries completed by concretors.
    Defined for server before initialization.
    '''
    __tablename__ = 'logbook_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    concretor_id = db.Column(db.Integer, db.ForeignKey("logbook_users.id"))
    site = db.Column(db.String(64))
    date = db.Column(db.Date)
    activity = db.Column(db.String(64))
    duration = db.Column(db.Integer, nullable=False)
    controls = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    #created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    #db.relationship("Student", back_populates="classes")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must unpack it's value
            # (when **kwargs is request.form, some values will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value) 
        set_attribute(self, "created_at", func.now())

    def __repr__(self):
        return f"CheckList({self.site}, {self.date}, {self.activity})"

    def __str__(self):
        return f"{self.job_site}, {self.display_date()}"

    def to_json(self):
        return {
            "site": self.site,
            "date": self.date,
            "activity": self.activity,
            "duration": self.duration,
            "controls": json.loads(self.controls),
            "created_at": self.created_at,
            "display date": self.display_date()
        }
    
    def display_date(self):
        return self.date.strftime('%A %d %B %Y')

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
          
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
    
    @classmethod
    def find_by_email(cls, email: str) -> "User":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str) -> "User":
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_concretor(cls, _id: int):
        #return cls.query.filter_by(concretor_id=_id).order_by(cls.date.desc()).all()
        return cls.query.filter_by(concretor_id=_id).order_by(cls.date.desc())

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return
