import json
import sqlite3

# Load JSON file
with open("questions_load.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

# Connect to SQLite database
conn = sqlite3.connect("trivia.db")
cursor = conn.cursor()

print(questions)
# Insert questions into the database
# for q in questions:
#     cursor.execute('''
#         INSERT INTO Questions (quest_type, quest_text, quest_ans, options, verified, sub_user, sub_date)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         q["quest_type"], 
#         q["quest_text"], 
#         q["quest_ans"], 
#         ', '.join(q["options"]),  # Convert list to string
#         q["verified"], 
#         q["sub_user"], 
#         q["sub_date"]
#     ))

# Commit and close the connection
conn.commit()
conn.close()

print("Questions inserted successfully!")
