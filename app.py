from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from datetime import date, datetime
import random
import secrets
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# I had a hard time making the number of questions dynamic - just hard-coding for now
num_questions = 3


# User login WTF form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Let’s Play Some Trivia!')


# WTF user signup form
class UserSetupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    userdob = DateField('Date of Birth', validators=[Optional()], render_kw={"placeholder": "YYYY-MM-DD", "value": date(2000, 1, 1).isoformat()})   
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('NB', 'Non-Binary'), ('O', 'Other')], validators=[Optional()])
    submit = SubmitField('Sign Up for Trivia!')


# Load all qustions from the SQlite DB
def load_questions():
    conn = sqlite3.connect('trivia.db')
    cursor = conn.cursor()

    # load and fetch all questions that are verfied (i.e. user-submitted questions need to be checked first)
    cursor.execute("SELECT quest_id, quest_type, quest_text, quest_ans, options FROM Questions WHERE verified=1")
    rows = cursor.fetchall()
    conn.close()

    # Convert each row into a dictionary
    # the options (possible answers) are in JSON format because they are just a list
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

# Pull random questions for the user's quiz
def get_random_questions():
    questions = load_questions()

    print(questions)
    print(type(questions))

    return random.sample(questions, num_questions)


# Search Wikipedia for articles about the questions subject matter
def search_wikipedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get("query", {}).get("search", [])
        if results:
            return [
                {"title": result['title'], "url": f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}"}
                for result in results[:2]  # Get top 2 results
            ]
    return [{"title": "No relevant Wikipedia articles found", "url": "#"}]


# WTF form to display the trivia questions and collect answers
class TriviaForm(FlaskForm):
    question_1 = RadioField('Question 1', choices=[], validators=[DataRequired()])
    question_2 = RadioField('Question 2', choices=[], validators=[DataRequired()])
    question_3 = RadioField('Question 3', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit Answers')


def format_options(options):
    # Convert list of MC options to title case for user-submitted Qs
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

    # sign in form (if they already have acct)
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # get username and password from db
        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, password FROM User WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        # Check password and save user info to session if valid
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect(url_for('index'))
        else:
            flash('Invalid username or password, please try again', 'danger')

    
    return render_template('index.html', form=form, username=None)


# To create new user acct
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSetupForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        birthdate = form.userdob.data
        password = form.password.data
        gender = form.gender.data

        conn = sqlite3.connect('trivia.db')
        cursor = conn.cursor()

        # Insert user data - encrypt the password
        cursor.execute("INSERT INTO User (username, password, email) VALUES (?, ?, ?)", (username, generate_password_hash(password), email))
        
        # return the user id to use as lookup for demo table
        user_id = cursor.lastrowid

        # Insert demographics data
        cursor.execute("INSERT INTO Demographics (user_id, dob, gender) VALUES (?, ?, ?)", 
                       (user_id, birthdate, gender))

        conn.commit()
        conn.close()
        session['user_id'] = user_id
        session['username'] = form.username.data


        return redirect(url_for('index'))

    return render_template('signup.html', form=form)

# Allow guests but don't create in db, just temporary - save in session only
@app.route('/guest_login')
def guest_login():
    session['username'] = f"Guest{random.randint(10000, 99999)}" # assign rando username
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

# create and administer the trivia quiz
@app.route('/trivia', methods=['GET', 'POST'])
def trivia():
    if 'username' not in session:
        return redirect(url_for('index'))  # Restart if session data is missing

    username = session['username']
    user_id = session.get('user_id', None)

    if user_id:  # Only store games for registered users, not guests
        if 'game_id' not in session:
            conn = sqlite3.connect('trivia.db')
            cursor = conn.cursor()

            cursor.execute("INSERT INTO game_header (user_id, status) VALUES (?, ?)", 
                           (user_id, 'in_progress'))
            
            session['game_id'] = cursor.lastrowid
            conn.commit()
            conn.close()



    # Only generate new questions if they are not already stored
    if 'selected_questions' not in session:
        selected_questions = get_random_questions()
        session['selected_questions'] = selected_questions
    else:
        selected_questions = session['selected_questions']

    form = TriviaForm()

    # shuffle the options for multiple choice (but not for T/F)
    for i in range(num_questions):
        if selected_questions[i]['quest_type'] == 'mc':
            random.shuffle(selected_questions[i]['options'])


    # Manually assign question text and choices
    # opt, opt is for value and name - wtf needs tuple, keep same
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


# check answers and give score
@app.route('/results')
def results():
    if 'selected_questions' not in session or 'user_answers' not in session:
        return redirect(url_for('index'))  # Prevent errors if session data is missing

    game_id = session['game_id']
    user_id = session.get('user_id')
    username = session['username']
    selected_questions = session['selected_questions']
    user_answers = session['user_answers']

    score = 0
    results_data = []  # Store each question, correct answer, and user answer

    conn = sqlite3.connect('trivia.db')
    cursor = conn.cursor()


    # Loop through the selected questions to compare answers
    for i, question in enumerate(selected_questions, start=1):
        question_key = f'question_{i}'
        correct_answer = question['quest_ans']
        user_answer = user_answers.get(question_key, '')

        # Check if the answer is correct
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1

        

        cursor.execute("INSERT INTO game_detail (game_id, question_id, correct) VALUES (?, ?, ?)", 
                (game_id, question['quest_id'], int(is_correct)))


        # get Wikipedia links for the question
        if question['quest_type'] == 'mc':
            wiki_links = search_wikipedia(question['quest_ans'])
        else:
            wiki_links = search_wikipedia(question['quest_text'])
            

        # Store question data for display
        results_data.append({
            'question_text': question['quest_text'],
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'wiki_links': wiki_links
        })

    # Update game status and duration
    start_time = cursor.execute("SELECT start_time FROM game_header WHERE game_id=?", (game_id,)).fetchone()[0]
    start_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    start_timestamp = int(start_time_obj.timestamp())

    duration = int(time.time()) - start_timestamp  # Calculate total time taken

    cursor.execute("UPDATE game_header SET status=?, duration=? WHERE game_id=?", 
                   ('completed', duration, game_id))

    conn.commit()
    conn.close()


    # Clear session so a new game starts next time
    session.pop('selected_questions', None)
    session.pop('user_answers', None)
    session.pop('game_id', None)

    return render_template('results.html', user_id=user_id, username=username, score=score, total=len(selected_questions), results_data=results_data)


# WIP - display varies starts for user and population
@app.route('/stats', methods=['GET','POST'])
def stats():
    return render_template('stats.html')



#############################################################################
################# USER CONTRIBUTED QUESTIONS
########### 
#############################################################################

@app.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if 'username' not in session or 'user_id' not in session: # check user_id too - guests shouldn't submit
        flash("Must be a registered user to submit questions", 'danger')
        return redirect(url_for('signup'))

    sub_user = session['user_id']

    if request.method == 'POST':
        question_type = request.form['question_type']
        question_text = request.form['question']
        
        if question_type == 't_f':  # default for True/False questions
            options = ["TRUE", "FALSE"]
        else:  # Multiple choice questions
            options = format_options([
                request.form['option1'],
                request.form['option2'],
                request.form['option3'],
                request.form['option4']
            ])
        

        # Convert to JSON for db storage
        options_json = json.dumps(options)

        # Store actual text of selected answer
        selected_option = request.form['correct_answer']  # e.g., "option1" or True/False
        
        
        if question_type == 't_f':  
            correct_answer = selected_option  # Just use "TRUE" or "FALSE" directly
        else:
            correct_answer = request.form[selected_option]  # Get actual text from form input

        # Insert into database
        # verified is 0 by default - need review first
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