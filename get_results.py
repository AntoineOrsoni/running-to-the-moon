import json
import time

import requests
import yaml

import toolbox.database as db
import toolbox.print_result as pr
import toolbox.ranking as rank
import toolbox.time as time

# Getting current timestamp
current_time = time.get_current_time()
current_week = time.get_week_number(current_time)
    
# Getting the raw output of the ranking
with open('credentials.yaml', 'r') as file:
    url_statistics = yaml.load(file, Loader = yaml.FullLoader)['url_statistics']

req = requests.get(url_statistics)

# Cure the data
ranking_current_total = rank.cure_teams(json.loads(req.text))

# Save in DB
db.add_output(json.dumps(ranking_current_total), 'total', current_week, current_time)

## Get the week results
ranking_current_week, old_time = rank.get_week_result(ranking_current_total, current_week - 1)
#pr.all_results(ranking_current_week)

db.add_output(json.dumps(ranking_current_week), 'week_result', current_week, current_time)

# Print the results
rank.get_best_average_distance_team(ranking_current_week, current_time, old_time)
rank.get_total_distance_team(ranking_current_week, current_time, old_time)
rank.get_best_runner_team(ranking_current_week, current_time, old_time)
rank.get_best_duo_height_team(ranking_current_week, current_time, old_time)
rank.get_best_duo_distance_team(ranking_current_week, current_time, old_time)
rank.get_best_average_activities_team(ranking_current_week, current_time, old_time)
