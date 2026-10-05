#!/usr/bin/python3
"""Unittests for the HBNB console"""
import os
import unittest
from io import StringIO
from unittest.mock import patch
from console import HBNBCommand
from models import storage


def run(cmd):
    """Run a console command and return its stripped output"""
    with patch('sys.stdout', new=StringIO()) as f:
        HBNBCommand().onecmd(cmd)
    return f.getvalue().strip()


class TestConsoleErrors(unittest.TestCase):
    """Tests for console error messages"""

    def test_create_missing_class(self):
        """create with no class name"""
        self.assertEqual(run("create"), "** class name missing **")

    def test_create_bad_class(self):
        """create with an unknown class"""
        self.assertEqual(run("create MyModel"), "** class doesn't exist **")

    def test_show_missing_class(self):
        """show with no class name"""
        self.assertEqual(run("show"), "** class name missing **")

    def test_show_bad_class(self):
        """show with an unknown class"""
        self.assertEqual(run("show MyModel 1"), "** class doesn't exist **")

    def test_show_missing_id(self):
        """show with no id"""
        self.assertEqual(run("show BaseModel"), "** instance id missing **")

    def test_destroy_missing_class(self):
        """destroy with no class name"""
        self.assertEqual(run("destroy"), "** class name missing **")

    def test_destroy_missing_id(self):
        """destroy with no id"""
        self.assertEqual(run("destroy BaseModel"),
                         "** instance id missing **")

    def test_all_bad_class(self):
        """all with an unknown class"""
        self.assertEqual(run("all MyModel"), "** class doesn't exist **")


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 "FileStorage only")
class TestConsoleFileStorage(unittest.TestCase):
    """Console tests that use FileStorage"""

    def tearDown(self):
        """Remove the storage file"""
        try:
            os.remove('file.json')
        except Exception:
            pass

    def get(self, cls, obj_id):
        """Return an object from storage"""
        return storage.all()[cls + "." + obj_id]

    def test_create_state(self):
        """create adds a new State to storage"""
        obj_id = run("create State")
        self.assertIn("State." + obj_id, storage.all())

    def test_create_then_show(self):
        """show prints an object that was created"""
        obj_id = run("create User")
        self.assertIn(obj_id, run("show User " + obj_id))

    def test_create_then_destroy(self):
        """destroy removes an object from storage"""
        obj_id = run("create Place")
        run("destroy Place " + obj_id)
        self.assertNotIn("Place." + obj_id, storage.all())

    def test_param_string(self):
        """string parameter is set"""
        obj_id = run('create State name="California"')
        self.assertEqual(self.get("State", obj_id).name, "California")

    def test_param_underscore_to_space(self):
        """underscores in strings become spaces"""
        obj_id = run('create Place name="My_little_house"')
        self.assertEqual(self.get("Place", obj_id).name, "My little house")

    def test_param_escaped_quote(self):
        """escaped double quotes are kept"""
        obj_id = run('create State name="My_\\"big\\"_state"')
        self.assertEqual(self.get("State", obj_id).name, 'My "big" state')

    def test_param_int(self):
        """integer parameter is set as int"""
        obj_id = run('create Place number_rooms=4')
        value = self.get("Place", obj_id).number_rooms
        self.assertEqual(value, 4)
        self.assertIs(type(value), int)

    def test_param_float(self):
        """float parameter is set as float"""
        obj_id = run('create Place latitude=37.773972')
        value = self.get("Place", obj_id).latitude
        self.assertEqual(value, 37.773972)
        self.assertIs(type(value), float)

    def test_param_negative_float(self):
        """negative float parameter is set"""
        obj_id = run('create Place longitude=-122.431297')
        self.assertEqual(self.get("Place", obj_id).longitude, -122.431297)

    def test_param_multiple(self):
        """several parameters are all set"""
        obj_id = run('create Place city_id="0001" max_guest=10 '
                     'price_by_night=300')
        obj = self.get("Place", obj_id)
        self.assertEqual(obj.city_id, "0001")
        self.assertEqual(obj.max_guest, 10)
        self.assertEqual(obj.price_by_night, 300)

    def test_param_invalid_skipped(self):
        """unquoted text, bad numbers and missing = are skipped"""
        obj_id = run('create State name=California size=1.2.3 '
                     'rank=abc nothing')
        obj = self.get("State", obj_id)
        self.assertNotIn('name', obj.__dict__)
        self.assertNotIn('size', obj.__dict__)
        self.assertNotIn('rank', obj.__dict__)

    def test_param_unescaped_quote_skipped(self):
        """a string with an unescaped quote inside is skipped"""
        obj_id = run('create State name="Cali"fornia"')
        self.assertNotIn('name', self.get("State", obj_id).__dict__)


if __name__ == "__main__":
    unittest.main()
