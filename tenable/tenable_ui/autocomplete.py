from flask import request, jsonify, current_app
from cache import cache

from tenable_ui.routes import game_bp
from tenable_ui.client import get_all_players


@cache.cached(key_prefix='player_list')
def player_list():
    response = get_all_players()
    players = response.get('players', [])

    if not players:
        current_app.logger.error('No response from player list')

    players_split = [p.split(' ', 1) for p in players]
    return players_split


@game_bp.route('/player_list', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').casefold()

    if not query:
        return jsonify([])
    
    players = player_list()
    filtered_list = [' '.join(p) for p in players if
                     p[0].casefold().startswith(query) or
                     (len(p) > 1 and p[1].casefold().startswith(query)) or
                      ' '.join(p).casefold().startswith(query)]
    
    return jsonify(filtered_list[:20])