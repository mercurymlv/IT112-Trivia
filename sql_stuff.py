import sqlite3

conn = sqlite3.connect('trivia.db')
cursor = conn.cursor()

# # ugh, add a comma so that it's a tuple
# new_users = [('Matthew',), ('Johnny',), ('Beth',)]

# cursor.executemany('''
#         INSERT INTO User (username) VALUES (?)
#     ''', new_users)

# conn.commit()  # Commit the changes

# cursor.execute("UPDATE User SET username='Johnny Boy' WHERE user_id=2")

cursor.execute("DELETE FROM User WHERE user_id=3")

conn.commit()

cursor.execute('SELECT * FROM User')
users = cursor.fetchall()
for user in users:
    print(user)

conn.close()   # Close the conn