import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

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

cursor.execute("DELETE FROM Questions WHERE quest_id=21")

# conn.commit()


cursor.execute('SELECT * FROM Questions')
quests = cursor.fetchall()
for q in quests:
    print(q)

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


conn.commit()
conn.close()   # Close the conn