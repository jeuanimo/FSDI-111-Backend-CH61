# ===================================
# BUDGET MANAGER API - Flask Backend
# ===================================
# This file creates a RESTful API for managing users in a budget management system
# It provides CRUD operations (Create, Read, Update, Delete) for user accounts

# Import required Flask modules and SQLite for database operations
from flask import Flask, jsonify
from flask import request
import sqlite3
from datetime import date

# Initialize Flask application instance
app = Flask(__name__)

# Database configuration - SQLite database file name
DB_NAME = "budget_manager.db"


# ===================================
# DATABASE INITIALIZATION FUNCTION
# ===================================
def init_db():
    """
    Initialize the database by creating the users table if it doesn't exist.
    This function is called when the application starts.
    
    Database Schema:
    - id: Primary key, auto-incrementing integer
    - username: Unique text field for user identification
    - password: Text field for user authentication (Note: In production, passwords should be hashed)
    """
    conn = sqlite3.connect(DB_NAME)  # Open a connection to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands

    # ----- Users Table Creation -----    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # ---------- EXPENSE TABLE CREATION ---------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount TEXT NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)  
        )
    ''')

    conn.commit()  # Save the changes to the database
    conn.close()  # Close the database connection

# ===================================
# API ENDPOINTS
# ===================================

# ===================================
# HEALTH CHECK ENDPOINT
# ===================================
@app.get("/api/health")
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    
    Returns:
        JSON response with status "healthy" and HTTP 200 status code
    
    Example Response:
        {
            "status": "healthy"
        }
    """
    return jsonify({"status": "healthy"}), 200


# ===================================
# USER REGISTRATION ENDPOINT
# ===================================
@app.post("/api/register")
def register_user():
    """
    Register a new user in the system.
    
    Expected JSON Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        - HTTP 201: Successfully created user
        - JSON response with success message
    
    Note: This endpoint doesn't validate for duplicate usernames or hash passwords
    """
    # Extract JSON data from the request body
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Connect to database and insert new user
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))  # Insert the new user into the users table
    conn.commit()  # Save the changes to the database
    conn.close()  # Close the database connection

    # Return success response
    return jsonify({
        "success": True,
        "message": "User registered successfully"
        }), 201


# ===================================
# USER LOGIN ENDPOINT
# ===================================
@app.post("/api/login")
def login_user():
    """
    Authenticate a user with username and password.
    
    Expected JSON Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        - HTTP 200: Successful login with user data
        - HTTP 401: Invalid credentials
    
    Example Success Response:
        {
            "user_id": 1,
            "username": "John"
        }
    
    Example Error Response:
        {
            "success": false,
            "message": "Invalid Credentials"
        }
    """
    # Extract login credentials from request
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Connect to database and search for user
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))  # Query the users table for the provided username 
    user = cursor.fetchone()  # Get the first matching user record
    conn.close()  # Close database connection

    # Check if user exists and password matches
    if user and user["password"] == password:
        # Successful authentication - return user data
        return jsonify({
            "user_is": user["id"],
            "username": user["username"],
            
        }), 200
    else:   
        # Invalid credentials - return error
        return jsonify({
            "success": False,
            "message": "Invalid Credentials"
        }), 401
# ===================================
# GET USER BY ID ENDPOINT
# ===================================
@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    """
    Retrieve a specific user by their ID.
    
    URL Parameters:
        user_id (int): The unique identifier of the user
    
    Returns:
        - HTTP 200: User found, returns user data
        - HTTP 404: User not found
    
    Example Success Response:
        {
            "id": 1,
            "username": "John"
        }
    
    Example Error Response:
        {
            "success": false,
            "message": "User not found"
        }
    """
    # Connect to database and search for user by ID
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # Query the users table for the provided user_id
    user = cursor.fetchone()  # Get the user record
    conn.close()  # Close database connection

    # Check if user exists and return appropriate response
    if user:
        # User found - return user data (excluding password for security)
        return jsonify({
            "id": user["id"],
            "username": user["username"]
        }), 200
    else:
        # User not found - return error
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
# ===================================
# UPDATE USER BY ID ENDPOINT
# ===================================
@app.put("/api/users/<int:user_id>")   
def update_user(user_id):
    """
    Update an existing user's information by their ID.
    
    URL Parameters:
        user_id (int): The unique identifier of the user to update
    
    Expected JSON Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        - HTTP 200: User successfully updated
        - HTTP 404: User not found
    
    Example Success Response:
        {
            "success": true,
            "message": "User updated successfully"
        }
    
    Example Error Response:
        {
            "success": false,
            "message": "User not found"
        }
    """
    # Extract updated user data from request
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # First, check if the user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # User exists, proceed with update
    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    conn.commit()  # Save the changes to the database
    conn.close()  # Close database connection

    # Return success response
    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200

# ===================================
# DELETE USER BY ID ENDPOINT
# ===================================
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    """
    Delete a user from the system by their ID.
    
    URL Parameters:
        user_id (int): The unique identifier of the user to delete
    
    Returns:
        - HTTP 200: User successfully deleted
        - HTTP 404: User not found
    
    Example Success Response:
        {
            "success": true,
            "message": "User Deleted successfully"
        }
    
    Example Error Response:
        {
            "success": false,
            "message": "User not found"
        }
    
    Warning: This operation is irreversible. The user data will be permanently removed.
    """
    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # First, check if the user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # User exists, proceed with deletion
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()  # Save the changes to the database
    conn.close()  # Close database connection

    # Return success response
    return jsonify({
        "success": True,
        "message": "User Deleted successfully"
    }), 200


# ===================================
# GET ALL USERS ENDPOINT
# ===================================
@app.get("/api/users")
def get_users():
    """
    Retrieve all users from the system.
    
    Returns:
        - HTTP 200: Successfully retrieved all users
        - JSON response with list of all users
    
    Example Success Response:
        {
            "success": true,
            "message": "Users retrieved successfully",
            "data": [
                {
                    "id": 1,
                    "username": "John",
                    "password": "password123"
                },
                {
                    "id": 2,
                    "username": "Jane",
                    "password": "securepass456"
                }
            ]
        }
    
    Note: In production, passwords should not be returned in API responses for security
    """
    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    
    # Execute query to get all users
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()  # Retrieve all user records
    conn.close()  # Close database connection

    # Convert database rows to list of dictionaries
    users = []
    for row in rows:
        user = {
            "id": row["id"],
            "username": row["username"],
            "password": row["password"]  # Note: In production, exclude passwords for security
        }
        users.append(user)
    
    # Return success response with user data
    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200


#----EXpenses------------
@app.post("/api/expenses")
def create_expense(): 
    data=request.get_json()
    title=data.get("title")
    description=data.get("description")
    amount=data.get("amount")
    date_str=date.today()
    category=data.get("category")
    user_id=data.get("user_id")

    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute('''
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, amount, date_str, category, user_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201



# ===================================
# APPLICATION STARTUP
# ===================================
if __name__ == "__main__":
    """
    Main application entry point.
    
    When this script is run directly (not imported as a module):
    1. Initialize the database by creating tables if they don't exist
    2. Start the Flask development server with debug mode enabled
    
    Debug mode features:
    - Auto-restart server when code changes
    - Detailed error messages in browser
    - Interactive debugger for exceptions
    
    Note: Debug mode should be disabled in production for security reasons
    """
    init_db()  # Initialize database tables
    app.run(debug=True)  # Start the Flask development server
