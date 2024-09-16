import pandas as pd
import os
import argparse
import csv
import sys
import json

from utilities.player_data import main as get_player_data
from utilities.two_teams_fix import main as format_two_team_rows
from utilities.validator import validate_output
# from country_codes import get_country_codes


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="To retrieve and format player data")
    parser.add_argument('-u', '--url', type=str, required=False, help='url for query')
    parser.add_argument('-off', '--max_offset', type=int, required=False, help='offset value for last page of query')
    parser.add_argument('-i', '--input', type=str, required=False, help='input file if needed, existing player_data')
    parser.add_argument('-o', '--output', type=str, required=True, help='filename for final csv')
    parser.add_argument('-tt', '--two_teams_fix', required=False, action='store_true', help='run two_teams_fix functions')
    parser.add_argument('-v', '--validate_output', required=False, action='store_true', help='option to validate formatted output')
    parser.add_argument('-in', '--index', required=False, action='store_true', help='create new integer player_id')

    args = parser.parse_args()

    if args.output:
        player_data_path = os.path.join(CURRENT_DIR, args.output)
        *dirs, _ = player_data_path.split('/')
        os.makedirs('/'.join(dirs), exist_ok=True)
    else:
        print('player_data.csv path not provided')
        print('exiting execution...')
        sys.exit(1)

    if args.input:
        input_path = os.path.join(CURRENT_DIR, args.input)
        player_data = pd.read_csv(input_path, names=HEADERS)
    elif args.url and args.max_offset:
        player_data = get_player_data(args.url, args.max_offset)
    else:
        print('Requires input file or URL and offset value...')
        print('exiting execution...')
        sys.exit(1)

    #### NOTES TO SELF
    #### add case for new rows to be added (concat) not to player_data but to df of big file (output)

    #### ALSO add these check and add these rows to savepoint file
    # Siren Diao, 2023-2024
    # José Díez Calleja, 1991-1992
    # Assane Dioussé, 2018-2019
    # Sylvain Distin, 2009-2010
    # Brice Dja Djédjé, 2013-2014
    # Nicola Ragagnin, 1991-1992

    # ADD A VALIDATOR TO COMPARE FILES AND CHECK NOTHING MISSING AFTER TWO TEAMS FIX


    if args.two_teams_fix:
        new_rows, blanks, errors = format_two_team_rows(player_data)
        save_new_rows(player_data=player_data, filename=args.output, new_rows=new_rows, blanks=blanks, errors=errors)

        if args.input:
            player_data = pd.read_csv(player_data_path, header=HEADERS)
            
        player_data = process_new_rows(player_data=player_data, new_rows=new_rows)
        
        if args.validate_output:
            print("Validating output files...")
            original_path = os.path.join(CURRENT_DIR, '_temp.'.join(args.output.split('.')))
            with open(original_path, 'r', encoding='utf-8') as original:
                message, missing = validate_output(original_file=original, formatted_file=player_data, column_names=HEADERS)
            print(message)
            message_path = os.path.join(CURRENT_DIR, args.output.split('.')[0] + '_validation.txt')
            with open(message_path, 'w') as validation_message:
                validation_message.write(message)
            print(f'Validation message saved to {message_path}')
            errors_path = os.path.join(CURRENT_DIR, args.output.split('.')[0] + '_errors.json')
            with open(errors_path, 'w') as errors_json:
                json.dump(missing, errors_json)
            print(f'Validation output saved to {errors_path}')
        col_format(player_data, args.index)
        player_data.sort_values(by=['player_id', 'Age'], inplace=True)

    player_data.to_csv(player_data_path, header=False, index=False)
    print(f'Output saved to {player_data_path}')
    print('Complete')


def save_new_rows(player_data: pd.DataFrame, filename: str, new_rows: list, blanks:list, errors: list):
    # new_rows, blanks, errors = format_two_team_rows(player_data)

    if not player_data.empty:
        player_data_path = '_temp.'.join(filename.split('.'))
        player_data.to_csv(os.path.join(CURRENT_DIR, player_data_path), header=False, index=False)

    if new_rows:
        new_rows_path = '_new_rows.'.join(filename.split('.'))
        with open(os.path.join(CURRENT_DIR, new_rows_path), 'w') as f:
            wr = csv.writer(f)
            wr.writerows(new_rows)

    if blanks:
        blanks_path = '_blanks.'.join(filename.split('.'))
        with open(os.path.join(CURRENT_DIR, blanks_path), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerows(blanks)

    if errors:
        errors_path = '_errors.'.join(filename.split('.'))
        with open(os.path.join(CURRENT_DIR, errors_path), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerows(errors)


def process_new_rows(player_data: pd.DataFrame,new_rows: list):
    indices = player_data[(player_data.Team == '2 Teams') | (player_data.Team == '3 Teams')].index.tolist()
    player_data.drop(indices, axis=0, inplace=True)
    player_data = pd.concat([player_data, pd.DataFrame(new_rows, columns=player_data.columns)])

    return player_data


def col_format(df: pd.DataFrame, reindex: bool = True):
    if reindex:
        unique_values = df.player_id.unique()
        value_to_int = {val: idx+1 for idx, val in enumerate(unique_values)}
        df.player_id = df.player_id.map(value_to_int)

    df.Age = pd.to_numeric(df.Age, errors='coerce')
    df.Age = df.Age.fillna(0)
    df.Age = df.Age.astype("int64")

    #split nation
    df.Nation = df.Nation.str.split().str[1]
    
    #split competition
    df.Comp = df.Comp.str.split().str[1:].str.join(' ')

    #int minutes
    df.Min = df.Min.str.replace(',','').replace('', 0)
    df.Min = df.Min.fillna(0)
    df.Min = df.Min.astype("int64")


if __name__ == "__main__":
    main()
