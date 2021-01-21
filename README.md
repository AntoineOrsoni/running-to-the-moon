# running-to-the-moon

This application gives each week result of the race to the moon. You should run the script every sunday. It will compare the results of the day when the script is run, with the oldest day from the previous week. First day of the week is Monday, last day is Sunday.

## Installation

### credentials.yaml

Create a `credentials.yaml` file in the same folder as `get_results.py`. Insert the below line. Replace the end of the URL with the API ressource to poll.

```yaml
url_statistics: https://api.definisher.fr/xxx/xxx
```

### Install librairies

The three below lines will create a virtual environment, active it, and install the required librairies to run the script.

```bash
python -m venv venv
source venv/bin/active
pip install -r requirements.txt
```

### Creating the database

The first below command will create the SQLite database file. The second below command will instanciate a table in the database, with the right headers. The two below commands should be run in the same folder as the `get_results.py`.

```bash
touch sqlite/statistics.db
python sqlite/init_database.py
```

### Executing the script for the first time

Run the below command to execute the script for the first time.

```bash
python get_results.py
```

It should give you the below error. It's expected, you can ignore it.

```bash
Traceback (most recent call last):
  File "get_results.py", line 29, in <module>
    ranking_current_week, old_time = rank.get_week_result(ranking_current_total, current_week - 1)
  File "/Users/anorsoni/Documents/Programmability/temp/running-to-the-moon/toolbox/ranking.py", line 88, in get_week_result
    ranking_old_total, timestamp_old = db.get_output_type('total', old_week_number % 54)
  File "/Users/anorsoni/Documents/Programmability/temp/running-to-the-moon/toolbox/database.py", line 57, in get_output_type
    timestamp = get_oldest_timestamp(week)
  File "/Users/anorsoni/Documents/Programmability/temp/running-to-the-moon/toolbox/database.py", line 49, in get_oldest_timestamp
    return fetch_one(command, filter)[3]
TypeError: 'NoneType' object is not subscriptable
```

### Checking the first output save worked

Run the below command from the same folder as `get_results.py`.

```bash
sqlite3 sqlite/statistics.db
SELECT * FROM statistics ;
```

The output should **not** be empty. If it's not empty, you successfuly saved your first output. Wait for the next week to run the script again, and compare with the the previous value. 

## Running the script every week

Each Sunday, run the below command.

```python
python get_results.py
```

It should print the output of the current week.