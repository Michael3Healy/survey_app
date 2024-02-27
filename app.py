from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Survey, Question, satisfaction_survey

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

responses = []

@app.route('/')
def start_survey():
    title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    responses = []
    return render_template('survey_start.html', title=title, instructions=instructions)

@app.route('/questions/<int:question_number>')
def show_questions(question_number):
    """Page showing each question with answer choices"""
    next_question = len(responses)

    # If the survey isn't over...
    if next_question < len(satisfaction_survey.questions):
        question = satisfaction_survey.questions[next_question]
        answers = question.choices

        # Redirect to correct question
        if question_number == next_question:
            return render_template('questions.html', question=question.question, answers=answers)
        else:
            flash('Attempted to access invalid question!', 'error')
            return redirect(f'/questions/{next_question}')

    # Otherwise, redirect to thank you page
    else:
        flash('Attempted to access invalid question!', 'error')
        return redirect('/thanks')



@app.route('/answer', methods=['POST'])
def recieve_answer():
    answer = request.form['answer']
    responses.append(answer)
    next_question = len(responses)

    if next_question < len(satisfaction_survey.questions):
        return redirect(f'/questions/{next_question}')
    else:
        return redirect('/thanks')

@app.route('/thanks')
def show_thanks():
    return render_template('thanks.html')