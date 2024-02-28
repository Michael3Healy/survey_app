from flask import Flask, request, render_template, redirect, flash, jsonify, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Survey, Question, surveys
from random import randint

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def choose_survey():
    '''Page to choose survey. Checks cookies for whether user has completed survey or not'''
    
    uncompleted_surveys = []
    for survey in surveys:
        if not request.cookies.get(f'completed_{survey}'):
            uncompleted_surveys.append(survey)

    if not uncompleted_surveys:
        flash('You have completed all surveys', 'error')

    return render_template('choose_survey.html', surveys=uncompleted_surveys)

@app.route('/survey_start')
def start_survey():
    '''Displays survey title, instructions, and button to start survey'''

    survey_title = request.args['survey']
    session['survey'] = survey_title
    survey = surveys[survey_title]

    instructions = survey.instructions
    return render_template('survey_start.html', title=survey_title.capitalize(), instructions=instructions)


@app.route('/reset-responses', methods=['POST'])
def reset_responses():
    '''Resets responses upon clicking start survey button, redirects to first question'''

    session['responses'] = {}
    return redirect('/questions/0')


@app.route('/questions/<int:question_number>')
def show_questions(question_number):
    """Page showing each question with answer choices"""

    survey_title = session['survey']
    survey = surveys[survey_title]
    next_question = len(session['responses'])
    allow_text = survey.questions[next_question].allow_text

    # If the survey isn't over...
    if next_question < len(survey.questions):
        
        question = survey.questions[next_question]
        answers = question.choices

        # Redirect to correct question
        if question_number == next_question:
            return render_template('questions.html', question=question.question, answers=answers, allow_text=allow_text)
        else:
            flash('Attempted to access invalid question!', 'error')
            return redirect(f'/questions/{next_question}')

    # Otherwise, redirect to thank you page
    else:
        flash('Attempted to access invalid question!', 'error')
        return redirect('/')


@app.route('/answer', methods=['POST'])
def recieve_answer():
    '''Receives the answer from form, adds it to session['responses'], and redirects to next page'''
    question = request.form['question']
    answer = [request.form['answer']]
    comments = request.form.get('comments')
    
    if comments:
        answer.append(comments)
    
    # Add answer to session responses list
    responses = session['responses']
    responses[question] = answer
    session['responses'] = responses

    # The index of the next question is the same as the number of questions already answered
    next_question = len(session['responses'])
    survey_title = session['survey']
    survey = surveys[survey_title]

    # If the survey isn't over, redirect to next question. Otherwise, redirect to thank you page
    if next_question < len(survey.questions):
        return redirect(f'/questions/{next_question}')
    else:
        return redirect('/thanks')


@app.route('/thanks')
def show_thanks():
    '''Final page, sets cookie to indicate user has already completed survey'''
    survey_title = session['survey']
    html = render_template('thanks.html')
    response = make_response(html)

    response.set_cookie(f'completed_{survey_title}', 'yes', max_age=30*24*60*60)

    return response