from prettytable import PrettyTable

def table_results(ranking: object):

    table = PrettyTable()

    # Building the header
    # | Place | Team | Distance
    table_header = ['Place']

    for key in ranking.result[1].keys():
        table_header.append(key.capitalize())

    table.field_names = table_header

    # Building the lines
    for key, value in ranking.result.items():
        table_line = list()
        table_line.append(key)
        
        for sub_key, sub_value in value.items():
            table_line.append(sub_value)

        table.add_row(table_line)

    print(f'---- Classement "{ranking.name}" ----')
    print(f'{ranking.wording},\nentre le {ranking.old_time.split()[0]} et le {ranking.current_time.split()[0]}.')
    print('')
    print(str(table))
    print('')
    print('')

def all_results(ranking: dict):
    for team, participants in ranking.items():
        print(f'-- {team} --')

        for index, value in enumerate(participants):
            print(f'{index}: {value}')
        print('')
        print('')