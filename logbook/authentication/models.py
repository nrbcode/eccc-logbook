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
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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
    created_at    = db.Column(db.DateTime, server_default=func.now())
    is_verified   = db.Column(db.Boolean, default=False) # Email verification status
    role          = db.Column(db.String(50), nullable=False, default='concretor') # concretor; foreman; admin; webmaster

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must unpack it's value
            # (when **kwargs is request.form, some values will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, property, value)
        #set_attribute(self, "created_at", func.now())
        
        # allocate access privileges
        if self.email == current_app.config['ADMIN_EMAIL']:
            set_attribute(self, "role", "admin")
        elif self.email in current_app.config['FOREMEN_EMAIL_LIST']:
            set_attribute(self, "role", "foreman")
    
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

    @classmethod
    def select_learners(cls, students):
        '''Retrieve students from selected concretors.'''
        return db.session.scalars(db.select(cls).where(cls.id.in_(students)))
    
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
            print("Database operation on logbook_users completed successfully.")
        #finally:            db.session.close()  # Clean up and release the connection resource

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
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
