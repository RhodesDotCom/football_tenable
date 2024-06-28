from flask import request, jsonify, current_app

from cache import cache
from tenable_ui.routes import game_bp
from tenable_ui.client import get_input_list


# @cache.cached(0 ,key_prefix='autocomplete')
def input_list(category):
    response = get_input_list(category)
    inputs = response.get(category, [])

    if not inputs:
        current_app.logger.error('No response from autocomplete list')

    return [i.split(' ') for i in inputs if i]


@game_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').casefold()
    category = request.args.get('category', '')

    if not query:
        return jsonify([])
    
    items = input_list(category)
    
    filtered_list = []
    query_len = len(query.split(' '))

    for item in items:
        item_len = len(item)
        
        if query_len > item_len:
            continue
        
        i = 0
        while i < item_len:
            new_string = ' '.join(item[i:]).casefold()
            if new_string.startswith(query):
                filtered_list.append(' '.join(item))
            i += 1


    return jsonify(filtered_list[:20])