from flask import render_template, request, session, current_app, jsonify
from unidecode import unidecode

from tenable_ui.routes import game_bp
from tenable_ui.games_map import challenges
import tenable_ui.games as games


def _build_session(game_info: dict):
    
    func = game_info.get('func')
    response, answers = func()

    session.clear()

    session['response'] = response
    session['correct_answers'] = answers
    session['question'] = game_info.get('name')
    session['category'] = game_info.get('category')
    session['lives'] = 3
    session['previous_guesses'] = list()
    session['correct_guesses'] = list()
    session['info'] = list()


def game_start(game_info: dict, origin: str):

    _build_session(game_info)

    return render_template(
        'tenable_ui/game.html',
        origin=origin,
        question=session.get('question'),
        category=session.get('category'),
        answers=session.get('correct_guesses', []),
        lives=session.get('lives', 3),
        info=[],
        game_over=False
    )


def game_guess(guess, origin: str):
    
    repeat, correct, answer = _check_guess(guess)

    previous_guesses = session.get('previous_guesses', [])
    previous_guesses.append(answer) if answer else previous_guesses.append(guess.title())
    session['previous_guesses'] = previous_guesses
    
    info = []
    if correct and answer:
        correct_guesses = session.get('correct_guesses', [])
        correct_guesses.append(answer)
        session['correct_guesses'] = correct_guesses
        
        info = get_info(answer)
    
    # If answer incorrect and not previously guessed, decrease lives
    elif not repeat:
        lives = session.get('lives', 0)
        session['lives'] = lives-1

    # When lives reach 0, game over
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
    correct_answers = session.get('correct_answers', [])

    answers = correct_guesses + [a for a in set(correct_answers) if a not in correct_guesses]

    return render_template(
        'tenable_ui/game.html',
        question=session.get('question'),
        answers=answers[:10],
        lives=0,
        game_over=False
    )


@game_bp.route('/get_info/<player>', methods=['GET'])
def get_info(player):
    category = session.get('category')
    # use games_map key category
    info = []
    answers = session.get('response', [])
    for dic in answers:
        if dic[category] == player:
            new_dic = dic.copy()
            new_dic.pop(category)
            current_app.logger.info(new_dic)
            info.append(new_dic)

    if request.method == 'GET':
        return jsonify(info)
    else:
        return info


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
