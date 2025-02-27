from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from datetime import date
import random
import secrets
from flask import session
import json
import sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
num_questions = 3


# user form for WTF
class UserSetupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    # email = EmailField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    userdob = DateField('Date of Birth', validators=[Optional()], default=date(2000, 1, 1))
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('NB', 'Non-Binary'), ('O', 'Other')], validators=[Optional()])
    submit = SubmitField('Let’s Play Some Trivia!')

# load the complete list of questions from the JSON file
def load_questions():
    try:
        with open('questions.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_random_questions():
    questions = load_questions()
    return random.sample(questions, num_questions)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserSetupForm()  # UserSetupForm for setting up trivia
    
    if form.validate_on_submit():
        session['username'] = form.username.data
        session['num_questions'] = num_questions

        # generate the questions and store in session
        session['selected_questions'] = get_random_questions()

        return redirect(url_for('trivia'))  # No need for URL params now

    return render_template('index.html', form=form)


@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    if 'username' not in session or 'num_questions' not in session:
        return redirect(url_for('index'))  # Start over if session data is missing

    username = session['username']
    selected_questions = session['selected_questions']

    print(username)
    print(selected_questions)

    return render_template('trivia.html', username=username, questions=selected_questions)


@app.route('/results')
def results():
    questions = session.get('selected_questions', [])
    username = session.get('username', 'Guest')
    
    # Calculate score or whatever logic you need here
    score = 3
    
    return render_template('results.html', username=username, score=score, questions=questions)



@app.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if request.method == 'POST':
        new_question = request.form['question']
        new_answer = request.form['answer']
        
        # Add to the JSON file
        questions = load_questions()
        questions.append({"question": new_question, "answer": new_answer})
        
        with open('questions.json', 'w') as file:
            json.dump(questions, file, indent=4)
        
        return render_template('contribute.html', message="Question added successfully!")
    
    return render_template('contribute.html')

if __name__ == '__main__':
    app.run(debug=True)