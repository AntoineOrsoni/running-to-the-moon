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

    for line in output:
        
        if bool(re.match('EKIPTL', line['code'])):
            line['code'] = 'Oracoeur'
        elif bool(re.match('TRANSFORMTL', line['code'])):
            line['code'] = 'Greffés et Amis des Greffés'
        elif bool(re.match('TL_HML', line['code'])):
            line['code'] = 'Hôpital Marie Lannelongue'
        elif bool(re.match('TL_SFT', line['code'])):
            line['code'] = 'Médecins Transplanteurs'
        elif bool(re.match('MICROSOFTTTL', line['code'])):
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

        if line['code'] not in result.keys():
            result[line['code']] = list()

        # Capitalize name and surname
        line['prenom'] = capitalize_name(line['prenom'])
        line['nom_de_famille'] = capitalize_name(line['nom_de_famille'])

        # str to int
        line['total_activites_solo'] = int(line['total_activites_solo'])

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
    pr.all_results(ranking_old_total)

    ranking_current_week = copy.deepcopy(ranking_current_total)

    for team, courreurs in ranking_current_week.items():
    
        for index, courreur_results in enumerate(courreurs):

            # If the key is a number, then substract current_week and old_week values. 
            # If value is a float, keep only two decimals
            # Else it's a string (name, surname), add it as is.
            try:
                ranking_current_week[team][index] = {key:   (courreur_results[key] - ranking_old_total[team][index].get(key, 0) 
                                                                if isinstance(courreur_results[key], int)
                                                            else round(courreur_results[key] - ranking_old_total[team][index].get(key, 0), 2) 
                                                                if isinstance(courreur_results[key], float)
                                                            else courreur_results[key])
                                                            for key in courreur_results}

            # The key doesn't exist in the previous week. No need to substract, we can leave it as is.
            except KeyError:
                pass
            except IndexError:
                pass
    


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

        best_distance = 0

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