# no 'empty' table should show up for both of these examples, and their dialect should be mysql.

cat settings_in_code.py | pydal2sql
cat settings_via_cli.py | pydal2sql mysql --tables person
