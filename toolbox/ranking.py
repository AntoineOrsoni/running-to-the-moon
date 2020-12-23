import re
import toolbox.database as db

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

        team_name = line['code']
        line.pop('code')
        result[team_name].append(line)
    
    return result


# Get a dict which shows the progress of each participant for the current week
# It's the diff between the current_week_total and old_week_total
# old_week_number is the week number used for the comparison with the current_week
def get_week_result(ranking_current_total: dict, old_week_number: int) -> dict:

    # Get the previous week from DB
    ranking_old_total, timestamp_old = db.get_output_type('total', old_week_number)

    # Init the ranking_current_week with the same key, structure
    ranking_current_week = ranking_current_total

    for team, courreurs in ranking_current_total.items():
    
        for index, courreur_results in enumerate(courreurs):

            # If the key is a number, then substract current_week and old_week values. 
            # If value is a float, keep only two decimals
            # Else it's a string (name, surname), add it as is.
            ranking_current_week[team][index] = {key:   (courreur_results[key] - ranking_old_total[team][index].get(key, 0) if isinstance(courreur_results[key], int)
                                                        else round(courreur_results[key] - ranking_old_total[team][index].get(key, 0), 2) if isinstance(courreur_results[key], float)
                                                        else courreur_results[key])
                                                        for key in courreur_results}

    return ranking_current_week