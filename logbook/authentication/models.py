# -*- encoding: utf-8 -*-
"""
User Data Model
"""
import hashlib
import jwt
from time import time

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.attributes import set_attribute

from logbook import db


class User(db.Model, UserMixin):

    __tablename__ = 'logbook_users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    pw_hash       = db.Column(db.String(128))
    firstname     = db.Column(db.String(64), nullable=True)
    lastname      = db.Column(db.String(64), nullable=True)
    address       = db.Column(db.String(64), nullable=True)
    bio           = db.Column(db.String(64), nullable=True)
    created_at    = db.Column(db.DateTime)
    verified      = db.Column(db.Boolean, default=False)  # Email verification status

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
        return self.username

    def to_json(self):
        return {
            "username": self.username,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "address": self.address,
            "bio": self.bio
        }

    def avatar(self, size: str = '300'):
        
        # Encode the email to lowercase and then to bytes
        email_encoded = self.email.lower().encode('utf-8')
        # Generate the SHA256 hash of the email
        digest = hashlib.sha256(email_encoded).hexdigest()        
        # construct url
        identicon_url = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

        return identicon_url

    @classmethod
    def find_by_email(cls, email: str) -> "User":

        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str) -> "User":

        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> "User":

        return cls.query.filter(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
          
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return self

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

    def update_user(self, details):
        for property, value in details.items():
            setattr(self, property, value)
            #print(f'property {property} set to {value}')
        db.session.commit()

    def generate_confirmation_token(self, expires_in=3600):
        
        # For jwt.encode(), expiration is provided as a time in UTC
        # It is set through the "exp" key in the data to be tokenized
        data = {"exp": time() + expires_in, "confirm_id": self.id}
        
        return jwt.encode(data, current_app.secret_key, algorithm="HS512")

    @staticmethod
    def confirm_token(token):
        try:
            # Ensure token valid and hasn't expired
            data = jwt.decode(token, current_app.secret_key, algorithms=["HS512"])
        except jwt.ExpiredSignatureError:
            return "Token has expired"
        except jwt.InvalidSignatureError as e:
            return "Invalid signature"
        except jwt.InvalidTokenError:
            return "Invalid token"

        return db.session.get(User, data.get("confirm_id"))
