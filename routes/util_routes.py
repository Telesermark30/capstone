from flask import Blueprint, render_template, request, redirect, url_for, session

util_bp = Blueprint('util', __name__)

@util_bp.route('/select_language', methods=['GET', 'POST'])
def select_language():
    if request.method == 'POST':
        session['language'] = request.form['language']
        return redirect(url_for('patient.select_nutritionist'))
    language = session.get('language', 'en')
    translations = {
        'en': {'title': 'SELECT YOUR LANGUAGE', 'english': 'English', 'cebuano': 'Cebuano'},
        'ceb': {'title': 'PILIA ANG IMONG GUSTO NA PINULUNGAN', 'english': 'INGLES', 'cebuano': 'CEBUANO'}
    }
    translated_text = translations.get(language, translations['en'])
    return render_template('select_language.html', title=translated_text['title'],
                           english=translated_text['english'], cebuano=translated_text['cebuano'])