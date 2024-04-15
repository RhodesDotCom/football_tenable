from flask import render_template, request, session, current_app
from unidecode import unidecode

from tenable_ui.routes import game_bp
from tenable_ui.client import get_golden_boot_winners, get_all_players


def log(*args):
    for a in args:
        current_app.logger.info(a)


@game_bp.before_request
def initiate_session_variables():
    # if not session.get('players'):
    #     session['players'] = get_all_players().get('players', [])
    if not session.get('question'):
        session['question'] = 'Premier League Golden Boot Winners'
    if not session.get('response'):
        response = get_golden_boot_winners()
        session['correct_answers'] = [d['player'] for d in response]
    if not session.get('lives'):
        session['lives'] = 3
    if not session.get('guesses'):
        session['guesses'] = []
    if not session.get('correct_guesses'):
        session['correct_guesses'] = []
    if not session.get('info'):
        session['info'] = []
        

@game_bp.route('/game', methods=['GET', 'POST'])
def game():

    if request.method == 'GET':
        session.clear()
        initiate_session_variables()

    if request.method == 'POST':

        guess = request.form.get('guess')
        repeat, correct, answer = check_guess(guess)

        guesses = session.get('guesses', [])
        guesses.append(answer) if answer else guesses.append(guess.title())
        session['guesses'] = guesses
        
        if correct and answer:
            correct_guesses = session.get('correct_guesses', [])
            correct_guesses.append(answer)
            session['correct_guesses'] = correct_guesses
        elif not repeat:
            lives = session.get('lives', 0)
            session['lives'] = lives-1

    if session.get('lives', 0) == 0:
        game_over = True
    else:
        game_over = False

    return render_template(
        'tenable_ui/game.html',
        question=session.get('question'),
        # players=session.get('players', []),
        answers=session.get('correct_guesses', []),
        lives=session.get('lives', 3),
        info=session.get('info', []),
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


def check_guess(guess):

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


def create_info(answer):
    response = session.get('response')

    info = []
    for dic in response:
        if dic['player'] == answer:
            info.append({'season': dic['season'], 'goals': dic['goals']})

    return info
