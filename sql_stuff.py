import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json

conn = sqlite3.connect('trivia.db')
cursor = conn.cursor()



# # ugh, add a comma so that it's a tuple
# new_users = [('Matthew',), ('Johnny',), ('Beth',)]

# demos = [(1, '1983-11-26', 'M'), (2, '2001-05-06', 'NB')]

# cursor.executemany('''
#         INSERT INTO User (username) VALUES (?)
#     ''', new_users)

# cursor.executemany('''
#         INSERT INTO Demographics (user_id, dob, gender) VALUES (?, ?, ?)
#     ''', demos)

# conn.commit()  # Commit the changes


# cursor.execute("UPDATE Questions SET quest_text='In _____________ did Kubla Khan a stately pleasure-dome decree.' WHERE quest_id=19")
# cursor.execute("select * from questions where quest_id=19")
# q = cursor.fetchall()
# print(q)

# cursor.execute("DELETE FROM Questions WHERE quest_id=21")


# cursor.execute("SELECT quest_id, verified FROM questions WHERE verified=0")
# cflag = cursor.fetchall()

# for f in cflag:
#     cursor.execute("UPDATE questions SET verified = ? WHERE quest_id = ?", (1, f[0]))




# cursor.execute('SELECT * FROM Questions where quest_id in (15,22)')
# quests = cursor.fetchall()
# for q in quests:
#     print(q)

# cursor.execute('ALTER TABLE User ADD COLUMN email TEXT')

# Fetch existing users
# cursor.execute('SELECT user_id, username FROM User')
# users = cursor.fetchall()

# # Update users with email and password
# for user in users:
#     user_id, username = user
#     # Generate a hashed password (e.g., username + '333' for the password)
#     hashed_password = generate_password_hash(username.strip() + '333')
#     # Create an email based on the username
#     email = username.strip() + '@testingemail.edu'

#     # Update the user with email and password
#     cursor.execute("UPDATE User SET email = ?, password = ? WHERE user_id = ?",
#                    (email, hashed_password, user_id))

# for user in users:
#     user_id, username = user
#     # Remove all spaces from the username and then generate password
#     clean_username = username.strip().replace(" ", "")
#     hashed_password = generate_password_hash(clean_username + '333')
#     email = clean_username + '@testingemail.edu'

#     # Update the user with email and password
#     cursor.execute("UPDATE User SET email = ?, password = ? WHERE user_id = ?",
#                    (email, hashed_password, user_id))

# cursor.execute("""
#     SELECT 
#         CASE 
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 1 AND 12 THEN 'Youngsters'
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 13 AND 19 THEN 'Teen'
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 20 AND 29 THEN '20-29'
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 30 AND 39 THEN '30-39'
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 40 AND 49 THEN '40-49'
#             WHEN (strftime('%Y', 'now') - strftime('%Y', Demographics.dob)) BETWEEN 50 AND 59 THEN '50-59'
#             ELSE '60+'
#         END AS age_group,
#         COUNT(game_detail.correct) AS total_answers,
#         SUM(game_detail.correct) AS correct_answers
#     FROM User
#     left join Demographics on user.user_id = Demographics.user_id
#     JOIN game_header ON User.user_id = game_header.user_id
#     Left JOIN game_detail ON game_header.game_id = game_detail.game_id
#     WHERE game_header.status = 'completed'
#     ANd Demographics.dob is not null
#     GROUP BY age_group
#     """)

# age_data = cursor.fetchall()

# print(age_data)


cursor.execute("select quest_id from Questions where verified=1")

qids = cursor.fetchall()

for i in qids:
    print(i[0])

conn.commit()
conn.close()   # Close the conn