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


if __name__ == "__main__":
    unittest.main()
