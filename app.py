from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, SelectField, PasswordField, RadioField
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
    userdob = DateField('Date of Birth', validators=[Optional()], render_kw={"placeholder": "YYYY-MM-DD", "value": date(2000, 1, 1).isoformat()})   
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('NB', 'Non-Binary'), ('O', 'Other')], validators=[Optional()])
    submit = SubmitField('Let’s Play Some Trivia!')

def load_questions():
    conn = sqlite3.connect('trivia.db')
    cursor = conn.cursor()

    # Fetch all questions from the database
    cursor.execute("SELECT quest_id, quest_type, quest_text, quest_ans, options FROM Questions")
    rows = cursor.fetchall()
    conn.close()

    # Convert each row into a dictionary
    questions = [
        {
            'quest_id': row[0],
            'quest_type': row[1],
            'quest_text': row[2],
            'quest_ans': row[3],
            'options': row[4].split(', ')  # Convert string back to list
        }
        for row in rows
    ]

    return questions

def get_random_questions():
    questions = load_questions()
    return random.sample(questions, num_questions)

class TriviaForm(FlaskForm):
    question_1 = RadioField('Question 1', choices=[], validators=[DataRequired()])
    question_2 = RadioField('Question 2', choices=[], validators=[DataRequired()])
    question_3 = RadioField('Question 3', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit Answers')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserSetupForm()  # UserSetupForm for setting up trivia
    
    if form.validate_on_submit():
        username = form.username.data
        birthdate = form.userdob.data
        gender = form.gender.data

        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()

        # Insert user data
        cursor.execute("INSERT INTO User (username) VALUES (?)", (username,))
        user_id = cursor.lastrowid  # Get the ID of the inserted user

        # Insert demographics data
        cursor.execute("INSERT INTO Demographics (user_id, dob, gender) VALUES (?, ?, ?)", 
                       (user_id, birthdate, gender))

        conn.commit()
        conn.close()
    
        session['username'] = form.username.data
        session['num_questions'] = num_questions

        # generate the questions and store in session
        session['selected_questions'] = get_random_questions()
        print(load_questions())

        return redirect(url_for('trivia'))  # No need for URL params now

    return render_template('index.html', form=form)


@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    if 'username' not in session or 'num_questions' not in session:
        return redirect(url_for('index'))  # Restart if session data is missing

    username = session['username']
    selected_questions = session['selected_questions']

    form = TriviaForm()

    # Manually assign question text and choices
    form.question_1.label.text = selected_questions[0]['quest_text']
    form.question_1.choices = [(opt, opt) for opt in selected_questions[0]['options']]
    
    form.question_2.label.text = selected_questions[1]['quest_text']
    form.question_2.choices = [(opt, opt) for opt in selected_questions[1]['options']]
    
    form.question_3.label.text = selected_questions[2]['quest_text']
    form.question_3.choices = [(opt, opt) for opt in selected_questions[2]['options']]

    if form.validate_on_submit():
        # Store answers in session for later processing
        session['user_answers'] = {
            'question_1': form.question_1.data,
            'question_2': form.question_2.data,
            'question_3': form.question_3.data,
        }
        return redirect(url_for('results'))

    return render_template('trivia.html', username=username, form=form)



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