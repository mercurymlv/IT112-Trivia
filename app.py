from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from datetime import date
import random
import secrets
from flask import session, flash
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
num_questions = 3


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up for Trivia!')


# user form for WTF
class UserSetupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    userdob = DateField('Date of Birth', validators=[Optional()], render_kw={"placeholder": "YYYY-MM-DD", "value": date(2000, 1, 1).isoformat()})   
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('NB', 'Non-Binary'), ('O', 'Other')], validators=[Optional()])
    submit = SubmitField('Let’s Play Some Trivia!')



def load_questions():
    conn = sqlite3.connect('trivia.db')
    cursor = conn.cursor()

    # Fetch all questions from the database
    cursor.execute("SELECT quest_id, quest_type, quest_text, quest_ans, options FROM Questions WHERE verified=1")
    rows = cursor.fetchall()
    conn.close()

    # Convert each row into a dictionary
    questions = [
        {
            'quest_id': row[0],
            'quest_type': row[1],
            'quest_text': row[2],
            'quest_ans': row[3],
            'options': json.loads(row[4])
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


def format_options(options):
    """ Convert list of MC options to title case. """
    return [opt.title() for opt in options]

#############################################################################
################# ROUTES START HERE
########### USER LOGIN/CONFIG STUFF
#############################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    # If user is already logged in, just greet them
    if 'username' in session:
        return render_template('index.html', username=session['username'])

    form = LoginForm()

    if form.validate_on_submit():  # If form is submitted & valid
        username = form.username.data
        password = form.password.data

        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()

        cursor.execute('SELECT user_id, username, password FROM User WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # Check password
            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect(url_for('index'))
        else:
            flash('Invalid username or password, please try again', 'danger')

        

    return render_template('index.html', form=form, username=None)  # No user logged in


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSetupForm()  # UserSetupForm for setting up trivia
    
    if form.validate_on_submit():
        username = form.username.data
        birthdate = form.userdob.data
        password = form.password.data
        gender = form.gender.data

        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()

        # Insert user data
        cursor.execute("INSERT INTO User (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
        
        user_id = cursor.lastrowid  # Get the ID of the inserted user

        # Insert demographics data
        cursor.execute("INSERT INTO Demographics (user_id, dob, gender) VALUES (?, ?, ?)", 
                       (user_id, birthdate, gender))

        conn.commit()
        conn.close()
        session['user_id'] = user_id
        session['username'] = form.username.data


        return redirect(url_for('index'))  # No need for URL params now

    return render_template('signup.html', form=form)

@app.route('/guest_login')
def guest_login():
    session['username'] = f"Guest{random.randint(10000, 99999)}"
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    flash("You've been logged out!", "info")
    return redirect(url_for('index'))


#############################################################################
################# TRIVIA QUESTIONS AND STATS
########### 
#############################################################################


@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    if 'username' not in session:
        return redirect(url_for('index'))  # Restart if session data is missing

    username = session['username']

    # Only generate new questions if they are not already stored
    if 'selected_questions' not in session:
        selected_questions = get_random_questions()
        session['selected_questions'] = selected_questions
    else:
        selected_questions = session['selected_questions']

    form = TriviaForm()

    for i in range(num_questions):
        if selected_questions[i]['quest_type'] == 'mc':
            random.shuffle(selected_questions[i]['options'])


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
    if 'selected_questions' not in session or 'user_answers' not in session:
        return redirect(url_for('index'))  # Prevent errors if session data is missing

    user_id = session.get('user_id')
    username = session['username']
    selected_questions = session['selected_questions']
    user_answers = session['user_answers']

    score = 0
    results_data = []  # Store each question, correct answer, and user answer

    # Loop through the selected questions to compare answers
    for i, question in enumerate(selected_questions, start=1):
        question_key = f'question_{i}'
        correct_answer = question['quest_ans']
        user_answer = user_answers.get(question_key, '')

        # Check if the answer is correct
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1

        # Store question data for display
        results_data.append({
            'question_text': question['quest_text'],
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'is_correct': is_correct
        })

    # Clear session so a new game starts next time
    session.pop('selected_questions', None)
    session.pop('user_answers', None)

    return render_template('results.html', user_id=user_id, username=username, score=score, total=len(selected_questions), results_data=results_data)

@app.route('/stats', methods=['GET','POST'])
def stats():
    return render_template('stats.html')



#############################################################################
################# USER CONTRIBUTED QUESTIONS
########### 
#############################################################################

@app.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if 'username' not in session or 'user_id' not in session:
        flash("Must be a registered user to submit questions", 'danger')
        return redirect(url_for('signup'))

    sub_user = session['user_id']

    if request.method == 'POST':
        question_type = request.form['question_type']
        question_text = request.form['question']
        
        if question_type == 'tf':  # True/False questions
            options = ["TRUE", "FALSE"]
        else:  # Multiple choice questions
            options = format_options([
                request.form['option1'],
                request.form['option2'],
                request.form['option3'],
                request.form['option4']
            ])
        
        # Convert to JSON for database storage
        options_json = json.dumps(options)

        # Fix: Store actual text of selected answer
        selected_option = request.form['correct_answer']  # e.g., "option1"
        correct_answer = request.form[selected_option]  # Get actual text

        # Insert into database
        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Questions (quest_type, quest_text, quest_ans, options, verified, sub_user, sub_date) 
            VALUES (?, ?, ?, ?, 0, ?, CURRENT_TIMESTAMP)
        ''', (question_type, question_text, correct_answer, options_json, sub_user))
        conn.commit()
        conn.close()

        return redirect(url_for('sub_confirmation'))

    return render_template('contribute.html')

@app.route('/sub_confirmation')
def sub_confirmation():
    return render_template('sub_confirmation.html')





if __name__ == '__main__':
    app.run(debug=True)