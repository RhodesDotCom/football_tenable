import pandas as pd
import os
import logging

from player_data import main as get_player_data
from two_teams_fix import main as format_two_team_rows
# from country_codes import get_country_codes


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def player_data():
    try:
        player_data = get_player_data()
        new_rows = format_two_team_rows(player_data)
        indices = player_data[player_data['Team'] == '2 Teams'].index.tolist()

        player_data.drop(indices, axis=0, inplace=True)
        player_data = pd.concat([player_data, pd.DataFrame(new_rows, columns=player_data.columns)], ignore_index=True)
        col_format(player_data)
        player_data.sort_values(by=['player_id', 'Age'], inplace=True)
    except Exception as e:
        print(e)
        players_csv = 'data/player_data_error.csv'
        csv_path = os.path.join(CURRENT_DIR, players_csv)
        player_data.to_csv(csv_path, header=False, index=False)
    finally:
        players_csv = 'data/all_players_formatted.csv'
        csv_path = os.path.join(CURRENT_DIR, players_csv)
        player_data.to_csv(csv_path, header=False, index=False)


def col_format(df):
    unique_values = df.player_id.unique()
    value_to_int = {val: idx+1 for idx, val in enumerate(unique_values)}
    df.player_id = df.player_id.map(value_to_int)

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


player_data()

