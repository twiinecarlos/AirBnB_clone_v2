#!/usr/bin/python3
"""Unittests for the DBStorage engine"""
import os
import unittest
from io import StringIO
from unittest.mock import patch

DB_MODE = os.getenv('HBNB_TYPE_STORAGE') == 'db'


@unittest.skipIf(not DB_MODE, "DBStorage only")
class TestDBStorage(unittest.TestCase):
    """Tests for DBStorage, checked with MySQLdb row counts"""

    @classmethod
    def setUpClass(cls):
        """Connect to the test database"""
        import MySQLdb
        from models import storage
        cls.storage = storage
        cls.db = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                                 user=os.getenv('HBNB_MYSQL_USER'),
                                 passwd=os.getenv('HBNB_MYSQL_PWD'),
                                 db=os.getenv('HBNB_MYSQL_DB'))

    @classmethod
    def tearDownClass(cls):
        """Close the database connection"""
        cls.db.close()

    def count(self, table):
        """Return the number of rows in a table"""
        self.db.commit()
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM {}".format(table))
        number = cur.fetchone()[0]
        cur.close()
        return number

    def make_state(self, name="California"):
        """Create and save a State"""
        from models.state import State
        state = State()
        state.name = name
        self.storage.new(state)
        self.storage.save()
        return state

    def test_new_and_save(self):
        """new + save adds a row to states"""
        before = self.count('states')
        self.make_state()
        self.assertEqual(self.count('states'), before + 1)

    def test_all_returns_dict(self):
        """all() returns a dict"""
        self.assertIsInstance(self.storage.all(), dict)

    def test_all_cls(self):
        """all(State) contains a saved State"""
        from models.state import State
        state = self.make_state("Nevada")
        self.assertIn('State.' + state.id, self.storage.all(State))

    def test_all_cls_string(self):
        """all('State') works with a class name"""
        state = self.make_state("Arizona")
        self.assertIn('State.' + state.id, self.storage.all('State'))

    def test_delete(self):
        """delete + save removes a row from states"""
        state = self.make_state("Texas")
        before = self.count('states')
        self.storage.delete(state)
        self.storage.save()
        self.assertEqual(self.count('states'), before - 1)

    def test_delete_none(self):
        """delete(None) does nothing"""
        before = self.count('states')
        self.storage.delete(None)
        self.storage.save()
        self.assertEqual(self.count('states'), before)

    def test_city(self):
        """saving a City adds a row to cities"""
        from models.city import City
        state = self.make_state("Oregon")
        before = self.count('cities')
        city = City()
        city.name = "Portland"
        city.state_id = state.id
        self.storage.new(city)
        self.storage.save()
        self.assertEqual(self.count('cities'), before + 1)

    def test_user(self):
        """saving a User adds a row to users"""
        from models.user import User
        before = self.count('users')
        user = User()
        user.email = "a@b.com"
        user.password = "pwd"
        self.storage.new(user)
        self.storage.save()
        self.assertEqual(self.count('users'), before + 1)

    def test_console_create_state(self):
        """console create State adds a row to states"""
        from console import HBNBCommand
        before = self.count('states')
        with patch('sys.stdout', new=StringIO()):
            HBNBCommand().onecmd('create State name="California"')
        self.assertEqual(self.count('states'), before + 1)


if __name__ == "__main__":
    unittest.main()
