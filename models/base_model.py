#!/usr/bin/python3
"""Defines the BaseModel class."""
import uuid
from os import getenv
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import models

if getenv("HBNB_TYPE_STORAGE") == "db":
    Base = declarative_base()
else:
    Base = object
time_fmt = "%Y-%m-%dT%H:%M:%S.%f"


class BaseModel:
    """Base class for all hbnb models."""
    id = Column(String(60), unique=True, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Instantiates a new model."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        for key, value in kwargs.items():
            if key == "__class__":
                continue
            if key in ("created_at", "updated_at") and isinstance(value, str):
                value = datetime.strptime(value, time_fmt)
            setattr(self, key, value)

    def __str__(self):
        """Returns a string representation of the instance."""
        d = self.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return "[{}] ({}) {}".format(type(self).__name__, self.id, d)

    def save(self):
        """Updates updated_at and saves the instance to storage."""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Returns a dictionary representation of the instance."""
        d = self.__dict__.copy()
        d["__class__"] = type(self).__name__
        for key in ("created_at", "updated_at"):
            if isinstance(d.get(key), datetime):
                d[key] = d[key].isoformat()
        d.pop("_sa_instance_state", None)
        return d

    def delete(self):
        """Deletes the current instance from storage."""
        models.storage.delete(self)
