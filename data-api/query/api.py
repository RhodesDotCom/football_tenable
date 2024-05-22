from flask import jsonify, current_app, Response, request

from query.routes import query_bp
from query.query import Queries


@query_bp.route('/get_inputs', methods=['GET'])
def get_inputs():
    category = request.args.get('category')
    queries = Queries()
    results = queries.get_inputs(category)
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response

@query_bp.route('/get_all_nations', methods=['GET'])
def get_all_nations():
    queries = Queries()
    results = queries.get_all_nationst()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response

@query_bp.route('/get_golden_boot_winners', methods=['GET'])
def get_golden_boot_winners():
    queries = Queries()
    results = queries.get_golden_boot_winners()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_goals_and_assists', methods=['GET'])
def get_goals_and_assist():
    goals = request.args.get('goals', 10)
    assists = request.args.get('assists', 10)
    queries = Queries()
    results = queries.get_goals_and_assists(goals, assists)
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_goals_by_nation', methods=['GET'])
def get_goals_by_nation():
    queries = Queries()
    results = queries.get_goals_by_nation()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response