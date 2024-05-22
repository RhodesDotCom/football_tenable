from flask import request, jsonify, current_app
from cache import cache

from tenable_ui.routes import game_bp
from tenable_ui.client import get_input_list


@cache.cached(0 ,key_prefix='autocomplete')
def input_list(category):
    response = get_input_list(category)
    current_app.logger.info(response)
    inputs = response.get(category, [])

    if not inputs:
        current_app.logger.error('No response from autocomplete list')

    inputs_split = [p.split(' ', 1) for p in inputs if p]
    return inputs_split


@game_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').casefold()
    category = request.args.get('category', '')

    if not query:
        return jsonify([])
    
    players = input_list(category)
    filtered_list = [' '.join(p) for p in players if
                     p[0].casefold().startswith(query) or
                     (len(p) > 1 and p[1].casefold().startswith(query)) or
                      ' '.join(p).casefold().startswith(query)]
    
    return jsonify(filtered_list[:20])