#!/usr/bin/python3
"""This module defines the DBStorage engine for the hbnb clone"""
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity

classes = {'State': State, 'City': City, 'User': User,
           'Place': Place, 'Review': Review, 'Amenity': Amenity}


class DBStorage:
    """Interacts with the MySQL database through SQLAlchemy"""
    __engine = None
    __session = None

    def __init__(self):
        """Creates the engine linked to the MySQL database"""
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                getenv('HBNB_MYSQL_USER'),
                getenv('HBNB_MYSQL_PWD'),
                getenv('HBNB_MYSQL_HOST'),
                getenv('HBNB_MYSQL_DB')),
            pool_pre_ping=True)
        if getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Returns a dictionary of objects, optionally filtered by class"""
        if cls is None:
            to_query = classes.values()
        else:
            if isinstance(cls, str):
                cls = classes.get(cls)
            if cls is None:
                return {}
            to_query = [cls]
        result = {}
        for model in to_query:
            for obj in self.__session.query(model).all():
                result[type(obj).__name__ + '.' + obj.id] = obj
        return result

    def new(self, obj):
        """Adds the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """Commits all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """Deletes obj from the current database session"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Creates all tables and a new database session"""
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)

    def close(self):
        """Closes the current session"""
        self.__session.remove()
