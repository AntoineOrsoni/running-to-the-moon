import re
import toolbox.database as db
import toolbox.print_result as pr
import copy

# Return capitalized name. Works for single names, names with a space, names with a `-`
def capitalize_name(name: str) -> str:

    splitter = str()
    result = str()

    if '-' in name:
        name = name.split('-')
        splitter = '-'
    else:
        name = name.split()
        splitter = ' '

    for sub_name in name:
        result += sub_name.capitalize() + splitter

    return result.strip(' -')

# Replace the random name for each team with a currated name
def cure_teams(output: list) -> list:

    result = dict()
    remove_doubles = ['MICROSOFTTL0002']

    for line in output:

        if line['code'] in remove_doubles:
            pass
        else:
            if bool(re.match('EKIPTL', line['code'])):
                line['code'] = 'Oracoeur'
            elif bool(re.match('TRANSFORMETL', line['code'])):
                line['code'] = 'Greffés et Amis des Greffés'
            elif bool(re.match('TL_HML', line['code'])):
                line['code'] = 'Hôpital Marie Lannelongue'
            elif bool(re.match('TL_SFT', line['code'])):
                line['code'] = 'Médecins Transplanteurs'
            elif bool(re.match('MICROSOFTTL', line['code'])):
                line['code'] = 'Microsoft'
            elif bool(re.match('TL_SCALITY', line['code'])):
                line['code'] = 'Scality'
            elif bool(re.match('SNCFTL', line['code'])):
                line['code'] = 'SNCF'
            elif bool(re.match('CHURouenTL', line['code'])):
                line['code'] = 'CHU Rouen'
            elif bool(re.match('TL_HP', line['code'])):
                line['code'] = 'HP'       
            elif bool(re.match('TL_EEX', line['code'])):
                line['code'] = 'EEX'           
            else:
                line['code'] = 'CAGIP'        

            # If the team doesn't not already exist in the currated_list
            # First runner. Create the team
            if line['code'] not in result.keys():
                result[line['code']] = list()

            # Capitalize name and surname
            line['prenom'] = capitalize_name(line['prenom'])
            line['nom_de_famille'] = capitalize_name(line['nom_de_famille'])

            # str to int
            line['total_activites_solo'] = int(line['total_activites_solo'])

            # 2 decimals
            line['total_distance_solo'] = round(line['total_distance_solo'], 2)

            # Remove old team code
            team_name = line['code']
            line.pop('code')
            result[team_name].append(line)
    
    return result


# Get a dict which shows the progress of each participant for the current week
# It's the diff between the current_week_total and old_week_total
# old_week_number is the week number used for the comparison with the current_week
def get_week_result(ranking_current_total: dict, old_week_number: int) -> dict:

    # Get the previous week from DB
    # modulo 54 allows to compare week 1 and week 52 as the previous week
    ranking_old_total, timestamp_old = db.get_output_type('total', old_week_number % 54)

    ranking_current_week = copy.deepcopy(ranking_current_total)

    for team, runners in ranking_current_week.items():
    
        for index, runner_results in enumerate(runners):
        
            old_index = 0

            # Find in the current_week the old_index of the name + surname (key 0, key 1) in the old_week. 
            # Save the old_index
            for i, old_runner_results in enumerate(ranking_old_total[team]):
                if all([x in old_runner_results.values() for x in list(runner_results.values())[:2]]):
                    old_index = i
                    break # Break once we find a match in the list, other runners won't match
                # the runner is new. Wasn't here in the old_week
                else: 
                    old_index = None

            ranking_current_week[team][index] = {key:   (runner_results[key]
                                                            if old_index == None # New runner. Don't substract, total_value = week_value
                                                        else runner_results[key] - ranking_old_total[team][old_index].get(key, 0) 
                                                            if isinstance(runner_results[key], int) # Substract
                                                        else round(runner_results[key] - ranking_old_total[team][old_index].get(key, 0), 2)
                                                            if isinstance(runner_results[key], float) # Substract and round with 2 decimals
                                                        else runner_results[key]) # It's a `str` key such as `name`. Don't substract
                                                        for key in runner_results}

    return (ranking_current_week, timestamp_old)


class Ranking:

    def __init__(self, name, wording, current_time, old_time):
        self.name = name
        self.wording = wording
        self.current_time = current_time
        self.old_time = old_time
        self.result = dict()

        for i in range (1,6):
            self.result[i] = dict()


def get_best_average_distance_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:

    name = 'Tais toi et marche'
    wording = 'Meilleure moyenne de km par équipe'
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        team_total = 0

        for participant in participants:
            team_total += participant['total_distance_solo']
        
        average = round(team_total / len(participants), 2)

        unsorted_results[team] = average

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['distance/part. (km)'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)


def get_total_distance_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:
    
    name = "Meilleure mobilisation d'équipe"
    wording = 'Total de km parcourus par équipe'
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        team_total = 0

        for participant in participants:
            team_total += participant['total_distance_solo']
        
        unsorted_results[team] = round(team_total, 2)

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['distance (km)'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)
    

def get_best_runner_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:
    
    name = "Cowboy.girl solitaire"
    wording = "Le.la meilleur.e performer.euse de l'équipe"
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        best_distance = 0.0

        for participant in participants:
            if participant['total_distance_solo'] > best_distance:
                best_distance = participant['total_distance_solo']
        
        unsorted_results[team] = round(best_distance, 2)

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['distance (km)'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)


def get_best_duo_height_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:
    
    name = "Tops Grimpeurs.ses"
    wording = "Les deux meilleurs.es grimpeurs.ses en cumul D+ de l'équipe"
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        best_height = []

        for participant in participants:
            if len(best_height) < 2:
                best_height.append(participant['total_denivele_solo'])
            else:
                if participant['total_denivele_solo'] > best_height[0]:
                    best_height[0] = participant['total_denivele_solo']
                elif participant['total_denivele_solo'] > best_height[1]:
                    best_height[1] = participant['total_denivele_solo']
                
        sum_height = round(best_height[0] + best_height[1], 0)
        unsorted_results[team] = round(sum_height, 0)

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['denivelé (m)'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)


def get_best_duo_distance_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:
    
    name = "Duo d'enfer"
    wording = "Les deux meilleurs.es coureurs.ses en cumul de km de l'équipe"
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        best_distance = []

        for participant in participants:
            if len(best_distance) < 2:
                best_distance.append(participant['total_distance_solo'])
            else:
                if participant['total_distance_solo'] > best_distance[0]:
                    best_distance[0] = participant['total_distance_solo']
                elif participant['total_distance_solo'] > best_distance[1]:
                    best_distance[1] = participant['total_distance_solo']
                
        sum_distance = round(best_distance[0] + best_distance[1], 2)
        unsorted_results[team] = round(sum_distance, 2)

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['distance (km)'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)


def get_best_average_activities_team(ranking_current_week: dict, current_time: str, old_time: str) -> dict:
    
    name = "Les Assidus"
    wording = "La meilleure moyenne de nombre de sorties par équipe"
    
    ranking = Ranking(name, wording, current_time, old_time)
    unsorted_results = dict()

    for team, participants in ranking_current_week.items():

        team_total = 0

        for participant in participants:
            team_total += participant['total_activites_solo']
        
        average = round(team_total / len(participants), 2)

        unsorted_results[team] = average

        sorted_results = dict(sorted(unsorted_results.items(), key=lambda item: item[1], reverse=True))

    for i in range(1,6):
        ranking.result[i]['team'] = list(sorted_results.keys())[i-1]
        ranking.result[i]['activités/part.'] = list(sorted_results.values())[i-1]

    pr.table_results(ranking)