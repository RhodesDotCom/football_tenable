import pandas as pd
import os
import argparse
import sys
import json
from typing import TextIO


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']


def main():
    parser = argparse.ArgumentParser(description="To retrieve and format player data")
    parser.add_argument('-fp1', '--filepath1', type=str, required=True, help="filepath for original file")
    parser.add_argument('-fp2', '--filepath2', type=str, required=True, help="filepath for formatted file")
    args = parser.parse_args()

    if not args.filepath1:
        print("original file path required.")
        print('Exiting...')
        sys.exit(1)
    if not args.filepath2:
        print("formatted file path required.")
        print('Exiting...')
        sys.exit(1)

    original_file = pd.read_csv(args.filepath1, names=HEADERS)
    formatted_file = pd.read_csv(args.filepath2, names=HEADERS)
    message, missing = validate_output(original_file, formatted_file, HEADERS)

    print(message)

    message_path = args.filepath1.split('.')[0] + '_validation.txt'
    with open(message_path, 'w') as validation_message:
        validation_message.write(message)
    print(f'Validation message saved to {message_path}')
    errors_path = args.filepath1.split('.')[0] + '_errors.json'
    with open(errors_path, 'w') as errors_json:
        json.dump(missing, errors_json)
    print(f'Validation output saved to {errors_path}')


def validate_output(original_file: TextIO | pd.DataFrame, formatted_file: TextIO | pd.DataFrame, column_names: list) -> tuple[bool, str, list | None]:
    
    of = original_file if isinstance(original_file, pd.DataFrame) else pd.read_csv(original_file, names=column_names)
    ff = formatted_file if isinstance(formatted_file, pd.DataFrame) else pd.read_csv(formatted_file, names=column_names)

    # if of['player_id'].dtype != 'int64':
    #     unique_values = of.player_id.unique()
    #     value_to_int = {val: idx+1 for idx, val in enumerate(unique_values)}
    #     of.player_id = of.player_id.map(value_to_int)

    two_teams_rows = of[(of.Team == '2 Teams') | (of.Team == '3 Teams')]
    message = ""
    missing = {}

    # COMPLETE CHECK
    message = check_file_lengths(of, ff, two_teams_rows, message)
    message, missing = check_normal_rows_exist(of, ff, message, missing)
    message, missing = check_2_team_rows(two_teams_rows, ff, message, missing)

    return message, missing
   

def check_file_lengths(of: pd.DataFrame, ff: pd.DataFrame, ttr: pd.DataFrame, message: str) -> str:
    original_file_length = len(of.index)
    formatted_file_length = len(ff.index)
    number_of_two_teams_rows = len(ttr.index)

    is_length_correct = (original_file_length == (formatted_file_length - number_of_two_teams_rows))

    if is_length_correct:
        message += "Formatted File is expected length.\n"
    elif original_file_length < (formatted_file_length + number_of_two_teams_rows):
        message += "Formatted file is bigger than expected.\n"
    elif original_file_length > (formatted_file_length + number_of_two_teams_rows):
        message += "Formatted file is smaller than expected.\n"
    
    return message


def check_normal_rows_exist(of: pd.DataFrame, ff: pd.DataFrame, message: str, missing: dict) -> tuple[str, dict]:
    non_two_teams_rows = of[(of.Team != '2 Teams') | (of.Team != '3 Teams')]

    merged_df = pd.merge(non_two_teams_rows[['player_id', 'player_name','Season']], ff[['player_id', 'player_name','Season']], how='left', indicator=True)
    
    do_all_normal_rows_exist = merged_df[merged_df['_merge'] == 'left_only'].size == 0

    if do_all_normal_rows_exist:
        message += "All NON two team row(s) exist in formatted file.\n"
    else:
        message += f"{merged_df[merged_df['_merge'] == 'left_only'].shape[0]} NON two team rows missing in formatted file.\n"
        missing["normal_rows"] = list(merged_df[merged_df['_merge'] == 'left_only'].itertuples(index=False, name=None))

    return message, missing


def check_2_team_rows(ttr: pd.DataFrame, ff: pd.DataFrame, message: str, missing: dict) -> tuple[str, dict]:

    ff_counts = ff[['player_id', 'player_name','Season']].groupby(['player_id', 'player_name','Season']).size().reset_index(name='count')
    merged_df = pd.merge(ttr[['player_id', 'player_name','Season']], ff_counts[['player_id', 'player_name','Season', 'count']], how='left', indicator=True)

    # TT ROWS DELETED IN FORMAT
    number_of_rows = merged_df[merged_df['_merge'] == 'left_only'].shape[0]
    message += f'{number_of_rows} row(s) missing from formatted file.\n'
    if number_of_rows:
        missing['ttr_missing'] = list(merged_df[merged_df['_merge'] == 'left_only'].itertuples(index=False, name=None))
    
    # ROWS NOT FORMATTED
    number_of_rows = merged_df[merged_df['count'] < 2].shape[0]
    message += f'{number_of_rows} incorrect row(s) in formatted file.\n'
    if number_of_rows:
        missing['ttr_not_formatted'] = list(merged_df[merged_df['count'] != 2].itertuples(index=False, name=None))

    return message, missing


if __name__ == "__main__":
    main()