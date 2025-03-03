import sqlite3

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

# cursor.execute("UPDATE Questions SET quest_text='The first president to live in the White House was' WHERE quest_id=20")

cursor.execute("DELETE FROM Questions WHERE quest_id=20")

# conn.commit()


cursor.execute('SELECT * FROM questions')
questions = cursor.fetchall()
for q in questions:
    print(q)


conn.close()   # Close the conn