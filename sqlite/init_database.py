# to be run from the parent directory

import sqlite3
db_connection = sqlite3.connect('sqlite/statistics.db')
db_cursor = db_connection.cursor()

# Setting up the database
## statistics table
db_cursor.execute('''CREATE TABLE statistics (output text, type text, week integer, timestamp text)''')

db_connection.commit()