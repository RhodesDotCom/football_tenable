from flask import render_template, request, session, current_app, jsonify
from unidecode import unidecode
import traceback

from tenable_ui.routes import game_bp
import tenable_ui.games as games


def build_game(origin: str, game_info: dict = {}, guess: str = None):

    if game_info:
        _build_session(game_info)
    
    info = []
    if guess:
        guess = guess.casefold()
        repeat, correct, answer = _check_guess(guess)
        _update_session('previous_guess', guess.title())

        if repeat:
            pass
        elif correct and answer:
            _update_session('correct_guesses', answer)
            info = get_info(answer)
        else:
            # If answer incorrect and not previously guessed, decrease lives
            lives = session.get('lives', 0)
            session['lives'] = lives-1
        
    
    if session.get('lives', 0) == 0:
        is_game_over = True
    else:
        is_game_over = False

    return render_template(
        'tenable_ui/game.html',
        origin=origin,
        question=session.get('question'),
        category=session.get('category'),
        answers=session.get('correct_guesses', []),
        lives=session.get('lives'),
        info=info,
        game_over=is_game_over
    )


@game_bp.route('/game_over', methods=['POST'])
def game_over():
    correct_guesses = session.get('correct_guesses', [])
    correct_answers = session.get('answers', [])

    answers = correct_guesses + [a for a in set(correct_answers) if a not in correct_guesses]

    return render_template(
        'tenable_ui/game.html',
        question=session.get('question'),
        answers=answers[:10],
        lives=0,
        game_over=False
    )


@game_bp.route('/get_info/<answer>', methods=['GET'])
def get_info(answer: str) -> list:
    category = session.get('category')
    # use game_info key --> category
    info = []
    answers = session.get('response', [])
    for dic in answers:
        if dic[category] == answer:
            new_dic = dic.copy()
            new_dic.pop(category)
            info.append(new_dic)

    if request.method == 'GET':
        return jsonify(info)
    else:
        return info


def _build_session(game_info: dict):
    current_app.logger.info('Changing session variables for new game...')
    try:
        func = game_info.get('func')
        response, answers = func()
    except Exception as e:
        current_app.logger.error(f'Error getting challenge function: {e}')
        current_app.logger.info(f'func: {func}, response: {response}, answers: {answers}')
    
    session.clear()

    session['response'] = response
    session['answers'] = answers
    session['question'] = game_info.get('name')
    session['category'] = game_info.get('category')
    session['lives'] = 3
    session['previous_guesses'] = list()
    session['correct_guesses'] = list()
    session['info'] = list()


def _check_guess(guess: str) -> tuple[bool, bool, str]:

    prev_guesses = session.get("previous_guesses")
    answers = session.get("answers")

    func = lambda x: x.casefold()

    repeat = True if guess.casefold() in list(map(func, prev_guesses)) else False
    correct = True if guess.casefold() in list(map(func, answers)) else False
    answer = guess.title() if correct else None
    
    return repeat, correct, answer


def _update_session(key: str, new_value: str):
    update = session.get(key)
    if update is not None:
        update.append(new_value)
        session[key] = update
