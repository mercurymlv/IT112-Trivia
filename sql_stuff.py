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

# cursor.execute("UPDATE User SET username='Johnny Boy' WHERE user_id=2")

# cursor.execute("DELETE FROM User WHERE user_id=3")

# conn.commit()

cursor.execute('ALTER TABLE Questions RENAME COLUMN quest_mc TO options;')

cursor.execute('SELECT * FROM User u left join Demographics d on u.user_id=d.user_id')
users = cursor.fetchall()
for user in users:
    print(user)


conn.close()   # Close the conn