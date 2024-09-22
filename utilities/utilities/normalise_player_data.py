import pandas as pd
import os
import sys
import argparse


HEADERS = ['player_id','player_name','Season','Age','Nation','Team','Comp','MP','Min','90s','Starts','Subs','unSub','Gls','Ast','G+A','G-PK','PK','PKatt','PKm','Pos']


def main():
    parser = argparse.ArgumentParser(description="Normalise player data")
    parser.add_argument('-i', '--input', type=str, required=True, help='player data file')
    parser.add_argument('-o', '--output', type=str, required=False, help='output directory')
    args = parser.parse_args()

    if args.input:
        player_data_path = args.input
    else:
        print("input CSV path required...")
        print("Exiting...")
        sys.exit(1)
    
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        output_path = args.output
    else:
        *dirs, _ = player_data_path.split('/')
        os.makedirs('/'.join(dirs), exist_ok=True)
        output_path = '/'.join(dirs)

    players_data = pd.read_csv(player_data_path, names=HEADERS)

    players, comp, player_season_stats = split_player_id(players_data)
    # print(output_path + 'players.csv')
    players.to_csv(output_path + '/players.csv', index=False, header=False)
    comp.to_csv(output_path + '/leagues.csv', index=False, header=False)
    player_season_stats.to_csv(output_path + '/season_stats.csv', index=False, header=False)


def split_player_id(players_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
           
    comp = players_data[['Comp']].drop_duplicates().reset_index(drop=True)
    comp.sort_values(by=["Comp"], inplace=True)
    comp.insert(0, 'competition_id', range(1, len(comp) + 1))

    players = players_data[['player_id','player_name','Nation']].drop_duplicates()

    player_season_stats = players_data.drop(columns=['player_name', 'Nation'])
    merged = pd.merge(player_season_stats, comp, on='Comp', how='left')
    player_season_stats['Comp'] = merged['competition_id']

    return players, comp, player_season_stats


if __name__ == "__main__":
    main()
