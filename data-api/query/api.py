from flask import jsonify, current_app, Response, request

from query.routes import query_bp
from query.query import Queries


def get_queries():
    queries = Queries()
    try:
        return queries
    finally:
        del queries


@query_bp.route('/get_inputs', methods=['GET'])
def get_inputs():
    category = request.args.get('category')
    queries = get_queries()
    results = queries.get_inputs(category)
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response

@query_bp.route('/get_all_nations', methods=['GET'])
def get_all_nations():
    queries = get_queries()
    results = queries.get_all_nationst()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response

@query_bp.route('/get_golden_boot_winners', methods=['GET'])
def get_golden_boot_winners():
    queries = get_queries()
    results = queries.get_golden_boot_winners()
    current_app.logger.info(results)
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_goals_and_assists', methods=['GET'])
def get_goals_and_assist():
    goals = request.args.get('goals', 10)
    assists = request.args.get('assists', 10)
    queries = get_queries()
    results = queries.get_goals_and_assists(goals, assists)
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_goals_by_nation', methods=['GET'])
def get_goals_by_nation():
    queries = get_queries()
    results = queries.get_goals_by_nation()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_goals_by_team', methods=['GET'])
def get_team_total_goals():
    queries = get_queries()
    results = queries.get_team_total_goals()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_team_topscorers_by_season', methods=['GET'])
def get_team_topscorers_by_season():
    queries = get_queries()
    results = queries.get_team_topscorers_by_season()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response


@query_bp.route('/get_team_topscorers_without_golden_boot', methods=['GET'])
def get_team_topscorers_without_golden_boot():
    queries = get_queries()
    results = queries.get_team_topscorers_without_golden_boot()
    response = Response(jsonify(results).response, status=200, mimetype='application/json')
    return response