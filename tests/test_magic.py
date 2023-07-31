from src.pydal2sql.magic import find_missing_variables, generate_magic_code


def test_find_missing():
    # Example usage:
    code_string = """
       from math import floor # ast.ImportFrom
       import datetime # ast.Import
       from pydal import * # ast.ImportFrom with *
       a = 1
       b = 2
       print(a, b + c)
       d = e + b
       f = d
       del f  # ast.Del
       print(f)
       xyz
       floor(d)
       ceil(d)
       ceil(e)

       datetime.utcnow()

       db = DAL()

       db.define_table('...')

       for table in []:
           print(table)

       if toble := True:
           print(toble)
       """

    missing_variables = find_missing_variables(code_string)
    assert missing_variables == {"c", "xyz", "ceil", "e", "f"}, missing_variables


def test_fix_missing():
    code = generate_magic_code({"bla"})

    assert "empty = Empty()" in code
    assert "bla = empty" in code