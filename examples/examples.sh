#!/bin/bash

# no 'empty' table should show up for both of these examples, and their dialect should be mysql.
cat settings_in_code.py | pydal2sql create
cat settings_via_cli.py | pydal2sql create mysql --tables person

# this file contains unknown variables, so only works with --magic:
pydal2sql create magic.py --magic
