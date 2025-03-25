import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("trivia.db")
cur = conn.cursor()

# Read CSV into Pandas DataFrame
df = pd.read_csv("load_detail.csv")

# Insert into game_header (SQLite will auto-fill game_id & start)
df.to_sql("game_detail", conn, if_exists="append", index=False)

print("game_detail data imported successfully!")

# Commit and close connection
conn.commit()
conn.close()
