# Tools

get_country_codes.py -> gets countries and their matching FIFA codes

get_formatted_player_data.py -> gets players from provided url and formats for database

normalise_player_data -> splits player data csv into normalised data



# How To Use

to run scripts within the docker container use:

docker-compose exec utilities python utilities/SCRIPT.py -args


# Examples


docker-compose exec utilities python utilities/get_formatted_player_data.py -u "https://stathead.com/fbref/player-season-finder.cgi?request=1&force_min_year=1&comp_type=b5&match=player_season&phase_id=0&per90_type=player&order_by=name_display_csk&per90min_val=5&order_by_asc=1&weight_type=kgs&height_type=height_meters&comp_gender=m&offset={offset}" -off 94400 -o "output/top_5_eu_leagues.csv" -tt -v -in

docker-compose exec utilities python utilities/get_formatted_player_data.py -i data/top_5_eu_leagues_v2_blanks.csv -o data/top_5_eu_leagues_v2_temp.csv -tt -in -v