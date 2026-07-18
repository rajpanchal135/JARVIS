
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# Restrict CORS to localhost origins only (security hardening)
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'jarvis.db')

def connect_db():
    con = sqlite3.connect(DB_PATH)
    return con

@app.route("/")
def server_index():
    return send_file("index.html")

@app.route('/test')
def test():
    return "Backend is working!"

# Add System Command API
@app.route('/add_system_command', methods=['POST'])
def add_system_command():
    data = request.json
    print("Received data:", data)

    con = connect_db()
    cursor = con.cursor()

    try:
        cursor.execute('INSERT INTO system_command (name, path) VALUES (?, ?)', (data['name'], data['path']))
        con.commit()
        message = 'Command added successfully!'
        print(message)
    except Exception as e:
        message = f'Error: {str(e)}'
        print(message)
    finally:
        con.close()

    return jsonify({'message': message})

# Get System Commands API
@app.route('/get_system_commands', methods=['GET'])
def get_system_commands():
    con = connect_db()
    cursor = con.cursor()

    try:
        cursor.execute('SELECT * FROM system_command')
        commands = [{'id': row[0], 'name': row[1], 'path': row[2]} for row in cursor.fetchall()]
        print("Fetched commands:", commands)
    except Exception as e:
        print(f"Error fetching commands: {str(e)}")
        commands = []

    con.close()
    return jsonify(commands)

# Add Web Command API
@app.route('/add_web_command', methods=['POST'])
def add_web_command():
    data = request.json
    print("Received web command data:", data)

    if 'name' not in data or 'url' not in data:
        print("Error: Missing 'name' or 'url' in request")
        return jsonify({'message': "Error: Missing 'name' or 'url'"}), 400

    con = connect_db()
    cursor = con.cursor()

    try:
        cursor.execute('INSERT INTO web_command (name, url) VALUES (?, ?)', (data['name'], data['url']))
        con.commit()
        message = 'Web command added successfully!'
        print(message)
    except Exception as e:
        message = f"Error: {str(e)}"
        print(message)
    finally:
        con.close()

    return jsonify({'message': message})


# Get Web Commands API
@app.route('/get_web_commands', methods=['GET'])
def get_web_commands():
    con = connect_db()
    cursor = con.cursor()

    try:
        cursor.execute('SELECT * FROM web_command')
        commands = [{'id': row[0], 'keyword': row[1], 'url': row[2]} for row in cursor.fetchall()]
        print("Fetched web commands:", commands)
    except Exception as e:
        print(f"Error fetching web commands: {str(e)}")
        commands = []

    con.close()
    return jsonify(commands)


# Delete record from system_command or web_command table
@app.route("/delete", methods=["POST"])
def delete_record():
    try:
        data = request.json
        table = data.get("table", "system_command")
        
        # Whitelist allowed table names to prevent SQL injection
        allowed_tables = ["system_command", "web_command"]
        if table not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        con = connect_db()
        cursor = con.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (data["id"],))
        con.commit()
        con.close()
        
        return jsonify({"message": f"Record with ID {data['id']} deleted successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
