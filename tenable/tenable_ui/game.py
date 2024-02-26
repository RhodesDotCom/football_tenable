from flask import render_template, request, session, current_app
from unidecode import unidecode

from tenable_ui.routes import game_bp
from tenable_ui.client import get_golden_boot_winners


@game_bp.route('/game', methods=['GET', 'POST'])
def game():
    current_app.logger.info(str(request.method))

    if request.method == 'GET':
        session['question'] = 'Premier League Golden Boot Winners'
        session['response'] = get_golden_boot_winners()

        session['guesses'] = []
        session['correct_answers'] = [d['player'] for d in session['response']]

    if request.method == 'POST':
        guess = request.form.get('guess')

        for answer in set(session.get('correct_answers', [])):
            if unidecode(guess.casefold()) == unidecode(answer.casefold()):
                guesses = session.get('guesses', [])
                guesses.append(answer)
                session['guesses'] = guesses

    return render_template(
        'tenable_ui/game.html',
        question=session.get('question'),
        answers=session.get('guesses', [])
    )
