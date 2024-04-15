from flask import jsonify, current_app, Response

from query.routes import query_bp
from query.query import Queries


@query_bp.route('/get_all_players', methods=['GET'])
def get_all_players():
    queries = Queries()
    results = queries.get_all_players()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_golden_boot_winners', methods=['GET'])
def get_golden_boot_winners():
    queries = Queries()
    results = queries.get_golden_boot_winners()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response