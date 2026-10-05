#!/usr/bin/python3
"""Tests for FileStorage.all(cls) and FileStorage.delete()"""
import os
import unittest
from models.engine.file_storage import FileStorage
from models.state import State
from models.user import User


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 "FileStorage only")
class TestFileStorageDelete(unittest.TestCase):
    """Tests for the all filter and delete method"""

    def setUp(self):
        """Create a storage instance"""
        self.fs = FileStorage()

    def tearDown(self):
        """Remove the storage file"""
        try:
            os.remove('file.json')
        except Exception:
            pass

    def test_all_no_cls_returns_dict(self):
        """all() returns a dict"""
        self.assertIsInstance(self.fs.all(), dict)

    def test_all_cls_filters(self):
        """all(State) returns only States"""
        state = State()
        user = User()
        self.fs.new(state)
        self.fs.new(user)
        states = self.fs.all(State)
        self.assertIn("State." + state.id, states)
        self.assertNotIn("User." + user.id, states)

    def test_all_cls_string(self):
        """all('State') works with a class name"""
        state = State()
        self.fs.new(state)
        self.assertIn("State." + state.id, self.fs.all("State"))

    def test_delete(self):
        """delete removes the object"""
        state = State()
        self.fs.new(state)
        self.fs.delete(state)
        self.assertNotIn("State." + state.id, self.fs.all())

    def test_delete_none(self):
        """delete(None) does nothing"""
        count = len(self.fs.all())
        self.fs.delete(None)
        self.assertEqual(len(self.fs.all()), count)

    def test_delete_twice(self):
        """deleting an object not in storage does not fail"""
        state = State()
        self.fs.new(state)
        self.fs.delete(state)
        self.fs.delete(state)
        self.assertNotIn("State." + state.id, self.fs.all())


if __name__ == "__main__":
    unittest.main()
