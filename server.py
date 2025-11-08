from flask import Flask, jsonify
from flask import request
import sqlite3


app = Flask(__name__)

DB_NAME = "budget_manager.db"


def init_db():
    conn = sqlite3.connect(DB_NAME) # Open a connection to the SQLite database
    cursor = conn.cursor() # Create a cursor object to execute SQL commands

# ----- Users Table -----    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit() # Save the changes to the database
    conn.close() # Close the database connection



@app.get("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.post("/api/register")
def register_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()# create a cursor object to execute SQL commands
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) # Insert the new user into the users table
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User registered successfully"
        }), 201

@app.post("/api/login")
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor() # create a cursor object to execute SQL commands
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,)) # Query the users table for the provided username 
    user = cursor.fetchone()
    conn.close()

    if user and user["password"] == password:

        return jsonify({
            "user_is": user["id"],
            "username": user["username"],
            
        }), 200
    else:   
        return jsonify({
            "success": False,
            "message": "Invalid Credentials"
        }), 401
    

@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor() # create a cursor object to execute SQL commands
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) # Query the users table for the provided user_id
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "id": user["id"],
            "username": user["username"]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
