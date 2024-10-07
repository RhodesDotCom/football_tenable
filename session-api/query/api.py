from flask import jsonify, current_app, Response, request
from uuid import uuid4

from query.query import Session
from query.routes import session_bp


def get_session():
    session = Session()
    try:
        return session
    finally:
        del session


@session_bp.route('/add_session_variable', methods=['POST'])
def add_session_variable():
    session_data = request.json.get('session_data')

    session = get_session()
    session_response = session.add_session_variable(data=session_data)

    if session_response[1] == 201:
        response = {
            'message': 'Session variable added successfully',
            'session_id': session_response[0][0]
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Error adding session variable',
            'session_id': None
        }
        return jsonify(response), session_response[1]


@session_bp.route('/read_session_variable', methods=['GET'])
def read_session_variable():
    session_id = request.args.get('session_id')
    session = get_session()
    data = session.read_session_variable(id=session_id)

    if data:
        return jsonify(data), 200

    
