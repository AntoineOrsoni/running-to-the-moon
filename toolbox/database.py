import sqlite3
import contextlib
import json

# Execute a single statement
def execute_statement(command: str, filter: tuple):
    with contextlib.closing(sqlite3.connect('sqlite/statistics.db')) as db_connection: # auto-closes
        with db_connection: # auto-commits
            with contextlib.closing(db_connection.cursor()) as db_cursor: # auto-closes
                db_cursor.execute(command, filter)


# Fetch one output from the database
def fetch_one(command: str, filter: tuple) -> tuple:
    with contextlib.closing(sqlite3.connect('sqlite/statistics.db')) as db_connection: # auto-closes
        with db_connection: # auto-commits
            with contextlib.closing(db_connection.cursor()) as db_cursor: # auto-closes
                db_cursor.execute(command, filter)
                result = db_cursor.fetchone()
    
    return result

# Add an `output` in the `statistics` table
def add_output(output: str, type: str, week: int, current_time: str):
    
    # Inserting a line in the `output` table
    command = 'INSERT INTO statistics VALUES (?,?,?,?)'
    filter = (output, type, week, current_time)

    execute_statement(command, filter)


# Get the older timestamp for a given week
# All test from the same batch will have the same timestamp. 
def get_oldest_timestamp(week: int):

    command = '''   SELECT * FROM statistics 
                            WHERE week = (?)
                            ORDER BY timestamp DESC
                            LIMIT 1'''
    filter = str(week)

    # Sample output of db_cursor.fetchone()
    #| output | type        | week | timestamp  |
    #| ------ | ----------- | ---- | ---------- |
    #| {json} | total       | 1    | dd:mm:yyyy |
    return fetch_one(command, filter)[3]


# Return the output for a specific test, oldest timestamp -- Only the `output` of the `type`
# Sample output
# {json}
def get_output_type(type: str, week: int):

    timestamp = get_oldest_timestamp(week)
    print(timestamp)

    command = '''   SELECT * FROM statistics
                            WHERE type = (?) AND week = (?) '''
    filter = (type, week)

    output = fetch_one(command, filter)[0]

    # Verify we've been able to get an output which is not empty
    if output is not None:
        return (json.loads(output), timestamp)
    else:
        raise ValueError(   f"output is empty. Check we have an output for :\n"
                            f"   - week = {week},\n"
                            f"   - type = {type},\n"
                            f"   - timestamp = {timestamp}")