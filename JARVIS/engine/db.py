import sqlite3
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "jarvis.db")

con = sqlite3.connect(db_path)
cursor = con.cursor()

# Creating table for system applications path
query = "CREATE TABLE IF NOT EXISTS system_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

# Creating table for web urls
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# Insert default command (only if not already present)
query = "INSERT OR IGNORE INTO system_command VALUES (null,'notepad', 'C:\\Windows\\notepad.exe')"
cursor.execute(query)
con.commit()

con.close()
print("Database initialized successfully.")
