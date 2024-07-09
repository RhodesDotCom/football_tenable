from flask import render_template, request, session, current_app, jsonify
from unidecode import unidecode

from tenable_ui.routes import game_bp
from tenable_ui.games_map import PL_games
import tenable_ui.games as games


def log(*args):
    for a in args:
        current_app.logger.info(a)


def initiate_session_variables(game_name=None):

    info = PL_games.get(game_name, {})

    if not session.get('question'):
        session['question'] = game_name

    if not session.get('category'):
        session['category'] = info.get('category')

    if not session.get('response'):
        func = info['func']
        response, answers = func()
        session['response'] = response
        session['correct_answers'] = answers

    if not session.get('lives'):
        session['lives'] = 3

    if not session.get('guesses'):
        session['guesses'] = []

    if not session.get('correct_guesses'):
        session['correct_guesses'] = []

    if not session.get('info'):
        session['info'] = []
        

@game_bp.route('/game/<game_name>', methods=['GET', 'POST'])
def game(game_name):

    if request.method == 'GET':
        session.clear()
        initiate_session_variables(game_name)

    if request.method == 'POST':

        guess = request.form.get('guess')
        repeat, correct, answer = _check_guess(guess)

        guesses = session.get('guesses', [])
        guesses.append(answer) if answer else guesses.append(guess.title())
        session['guesses'] = guesses
        
        if correct and answer:
            correct_guesses = session.get('correct_guesses', [])
            correct_guesses.append(answer)
            session['correct_guesses'] = correct_guesses
            
            if session.get('category') == 'player':
                info = _create_info(answer)
            else:
                info = []
        
        # If answer incorrect and not previously guessed, decrease lives
        elif not repeat:
            lives = session.get('lives', 0)
            session['lives'] = lives-1

    # When lives reach 0, game over
    if session.get('lives', 0) == 0:
        game_over = True
    else:
        game_over = False


    return render_template(
        'tenable_ui/game.html',
        game_name=game_name,
        question=session.get('question'),
        category=session.get('category', None),
        answers=session.get('correct_guesses', []),
        lives=session.get('lives', 3),
        info=info if 'info' in locals() else [],
        game_over=game_over
    )


@game_bp.route('/game_over', methods=['POST'])
def game_over():
    correct_guesses = session.get('correct_guesses', [])
    correct_answers = session.get('correct_answers', [])

    answers = correct_guesses + [a for a in set(correct_answers) if a not in correct_guesses]

    return render_template(
        'tenable_ui/game.html',
        question=session.get('question'),
        answers=answers[:10],
        lives=0,
        game_over=False
    )


def _check_guess(guess):

    repeat = False
    correct = False
    answer = None

    if len(guess.split()) > 2:
        surname = ' '.join(guess.split()[-2:])
    else:
        surname = guess.split()[-1]

    for name in set(session.get('correct_answers', [])):
            if guess in session.get('guesses', []):
                repeat = True
                continue
            if unidecode(guess.casefold()) == unidecode(name.casefold()): # match guess without accents + case insensitive
                correct = True
                answer = name
                break
            if len(name.split()) > 2:
                if surname == ' '.join(name.split()[-2:]):
                    correct = True
                    answer = name
                    break
            else:
                if surname == name.split()[-1]:
                    correct = True
                    answer = name
                    break

    return repeat, correct, answer


##### CONSOLIDATE FUNCTIONS
def _create_info(answer):
    answers = session.get('response', [])
    
    info = []

    for dic in answers:
        if dic['player_name'] == answer:
            info.append({'season': dic['season'], 'goals': dic['goals']})

    return info


@game_bp.route('/get_info/<player>', methods=['GET'])
def get_info(player):
    info = []
    answers = session.get('response', [])
    for dic in answers:
        if dic['player_name'] == player:
            info.append({'season': dic['season'], 'goals': dic['goals']})
    return jsonify(info)