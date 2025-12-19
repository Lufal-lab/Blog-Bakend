# tests/test_db_check.py
from django.db import connection

def test_which_database_is_used():
    print("\nDATABASE NAME:", connection.settings_dict["NAME"])
    assert True