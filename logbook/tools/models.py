# -*- encoding: utf-8 -*-
"""
Tool Register Tables
"""

#from email.policy import default
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.attributes import set_attribute

from logbook import db


class RegisteredTool(db.Model):

    __tablename__ = 'tool_register'

    id            = db.Column(db.Integer, primary_key=True)
    brand_name    = db.Column(db.String(64))
    model_number  = db.Column(db.String(64))
    tool_name     = db.Column(db.String(64))
    tool_type     = db.Column(db.String(64))
    serial_num    = db.Column(db.String(64))
    ht_num        = db.Column(db.String(64)) # Hilti Tracking Number
    tool_notes    = db.Column(db.Text)
    added_at      = db.Column(db.DateTime, server_default=func.now())
    added_by      = db.Column(db.Integer, db.ForeignKey("logbook_users.id"))
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)
        #set_attribute(self, "added_at", func.now())

    def __repr__(self):
        return f'RegisteredTool(tool_name={self.tool_name}, brand_name={self.brand_name}, model_number={self.model_number})'

    def __str__(self):
        return f'{self.brand_name} {self.tool_name} added {self.added_at.strftime('%A %d %B %Y')}'

    def to_json(self):
        # DateTime cannot be serialized
        return {
            "tool name": self.tool_name,
            "brand name": self.brand_name,
            "model number": self.model_number,
            "tool type": self.tool_type
        }

    @classmethod
    def find_by_id(cls, tool_id: int) -> "RegisteredTool":
        '''Retrieve tool.'''
        return cls.query.filter_by(id=tool_id).first()

    @classmethod
    def find_by_concretor(cls, concretor_id: int) -> List["RegisteredTool"]:
        '''Find all tools registered by one concretor.'''
        return cls.query.filter_by(added_by=concretor_id).all()

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
        #finally:db.session.close()  # Clean up and release the connection resource
        
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


class CordedTool(RegisteredTool):

    __tablename__ = 'corded_tools'

    id = db.Column(db.Integer, db.ForeignKey("tool_register.id"), primary_key=True)
    tag_id = db.Column(db.Integer) # current tag
    updated_at = db.Column(db.DateTime, onupdate=func.now()) # tag is changed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #set_attribute(self, "tag_id", None)
    
    def update_tag(self, tag_id):
        set_attribute(self, "tag_id", tag_id)
        db.session.commit()


class CordedToolTag(db.Model):

    __tablename__ = 'tool_tags'

    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("corded_tools.id"))
    tag_num = db.Column(db.Integer, nullable=True)
    tag_date = db.Column(db.DateTime)
    next_test = db.Column(db.DateTime)

    def __str__(self):
        return f'Tool No.{self.tool_id} tagged {self.tag_date.strftime('%d/%m/%Y')}.'

    @classmethod
    def find_by_toolid(cls, tool: int) -> "CordedToolTag":

        return db.session.scalar(db.select(cls).filter_by(tool_id=tool).order_by(-cls.id))

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
        #finally:db.session.close()  # Clean up and release the connection resource
        

class ImagekitFile(db.Model):
    
    __tablename__ = 'tool_images'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey("tool_register.id"))
    file_id = db.Column(db.String(64), unique = True)
    file_url = db.Column(db.String(128), unique = True) # ImageKit CDN URL for the file
    upload_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    @classmethod
    def find_by_toolbox(cls, toolbox: List):
        '''
        Take a list of id numbers for registered tools,
        return pairs with key tool_id and value file_url or None.
        '''
        return db.session.scalars(db.select(cls.file_url).where(cls.tool_id in toolbox))

    @classmethod
    def find_by_toolid(cls, tool: int):
        return db.session.scalar(db.select(cls).filter_by(tool_id=tool))

    def __repr__(self):
        return f"ImagekitFile(tool_id={self.tool_id}, file_id={self.file_id}, file_url={self.file_url})"

    def __str__(self):
        return f"id: {self.tool_id}, file name:{self.file_id}, file url: {self.file_url})"

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
        #finally:db.session.close()  # Clean up and release the connection resource

    def update_image(self, details):

        self.file_id = details.get('file_id')
        self.file_url = details.get('file_url')
        self.upload_timestamp = func.now()
        db.session.commit()
