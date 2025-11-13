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
from constants import (SQL_SELECT_ALL_USER, 
                       SQL_DELETE_USER, 
                       SQL_INSERT_USER, 
                       SQL_UPDATE_USER,
                       SQL_SELECT_USER_BY_ID,
                       SQL_SELECT_ALL_EXPENSES,
                       SQL_SELECT_EXPENSE_BY_ID,
                       SQL_INSERT_EXPENSE,
                       SQL_UPDATE_EXPENSE,
                       SQL_DELETE_EXPENSE,
                       VALID_EXPENSE_CATEGORIES)
from responses import success_response, not_found_response

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
        JSON response with success format and HTTP 200 status code
    
    Example Response:
        {
            "success": true,
            "message": "API is healthy",
            "data": null
        }
    """
    return success_response("API is healthy")


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
    cursor.execute(SQL_INSERT_USER, (username, password))  # Insert the new user into the users table
    conn.commit()  # Save the changes to the database
    conn.close()  # Close the database connection

    # Return success response
    return success_response("User registered successfully")


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
        user_data = {
            "user_id": user["id"],
            "username": user["username"]
        }
        return success_response("Login successful", user_data)
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
    cursor.execute(SQL_SELECT_USER_BY_ID, (user_id,))  # Query the users table for the provided user_id
    user = cursor.fetchone()  # Get the user record
    conn.close()  # Close database connection

    # Check if user exists and return appropriate response
    if user:
        # User found - return user data (excluding password for security)
        user_data = {
            "id": user["id"],
            "username": user["username"]
        }
        return success_response("User retrieved successfully", user_data)
    else:
        # User not found - return error
        return not_found_response("User")
          
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
    cursor.execute(SQL_SELECT_USER_BY_ID, (user_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found_response("User")

    # User exists, proceed with update
    cursor.execute(SQL_UPDATE_USER, (username, password, user_id))
    conn.commit()  # Save the changes to the database
    conn.close()  # Close database connection

    # Return success response
    return success_response("User updated successfully")

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
    cursor.execute(SQL_SELECT_USER_BY_ID, (user_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found_response("User")

    # User exists, proceed with deletion
    cursor.execute(SQL_DELETE_USER, (user_id,))
    conn.commit()  # Save the changes to the database
    conn.close()  # Close database connection

    # Return success response
    return success_response("User deleted successfully")


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
    cursor.execute(SQL_SELECT_ALL_USER)
    rows = cursor.fetchall()  # Retrieve all user records
    conn.close()  # Close database connection

    # Convert database rows to list of dictionaries
    users = []
    for row in rows:
        user = {
            "id": row["id"],
            "username": row["username"]
        }
        users.append(user)
    
    # Return success response with user data
    return success_response("Users retrieved successfully", users)


# ===================================
# EXPENSES CRUD ENDPOINTS
# ===================================

# ===================================
# GET ALL EXPENSES ENDPOINT
# ===================================
@app.get("/api/expenses")
def get_all_expenses():
    """
    Retrieve all expenses from the system.
    
    Returns:
        - HTTP 200: Successfully retrieved all expenses
        - JSON response with list of all expenses
    
    Example Success Response:
        {
            "success": true,
            "message": "Expenses retrieved successfully",
            "data": [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "Lunch",
                    "amount": "25.50",
                    "category": "Food",
                    "date": "2025-11-12",
                    "description": "Business lunch meeting"
                }
            ]
        }
    """
    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    cursor = conn.cursor()
    
    # Execute query to get all expenses
    cursor.execute(SQL_SELECT_ALL_EXPENSES)
    rows = cursor.fetchall()
    conn.close()

    # Convert database rows to list of dictionaries
    expenses = []
    for row in rows:
        expense = {
            "id": row["id"],
            "user_id": row["user_id"],
            "title": row["title"],
            "amount": row["amount"],
            "category": row["category"],
            "date": row["date"],
            "description": row["description"]
        }
        expenses.append(expense)
    
    return success_response("Expenses retrieved successfully", expenses)


# ===================================
# GET EXPENSE BY ID ENDPOINT
# ===================================
@app.get("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    """
    Retrieve a specific expense by its ID.
    
    URL Parameters:
        expense_id (int): The unique identifier of the expense
    
    Returns:
        - HTTP 200: Expense found, returns expense data
        - HTTP 404: Expense not found
    
    Example Success Response:
        {
            "success": true,
            "message": "Expense retrieved successfully",
            "data": {
                "id": 1,
                "user_id": 1,
                "title": "Lunch",
                "amount": "25.50",
                "category": "Food",
                "date": "2025-11-12",
                "description": "Business lunch meeting"
            }
        }
    """
    # Connect to database and search for expense by ID
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(SQL_SELECT_EXPENSE_BY_ID, (expense_id,))
    expense = cursor.fetchone()
    conn.close()

    # Check if expense exists and return appropriate response
    if expense:
        expense_data = {
            "id": expense["id"],
            "user_id": expense["user_id"],
            "title": expense["title"],
            "amount": expense["amount"],
            "category": expense["category"],
            "date": expense["date"],
            "description": expense["description"]
        }
        return success_response("Expense retrieved successfully", expense_data)
    else:
        return not_found_response("Expense")


# ===================================
# CREATE EXPENSE ENDPOINT
# ===================================
@app.post("/api/expenses")
def create_expense():
    """
    Create a new expense in the system.
    
    Expected JSON Request Body:
        {
            "title": "string",
            "description": "string",
            "amount": "string",
            "category": "Food|Education|Entertainment",
            "user_id": integer
        }
    
    Returns:
        - HTTP 200: Successfully created expense
        - HTTP 400: Invalid category or missing data
    
    Note: Date is automatically set to today's date
    """
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")
    user_id = data.get("user_id")
    date_str = date.today()

    # Validate category
    if category not in VALID_EXPENSE_CATEGORIES:
        return jsonify({
            "success": False,
            "message": f"Invalid category. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
        }), 400

    # Connect to database and insert new expense
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(SQL_INSERT_EXPENSE, (user_id, title, amount, category, date_str, description))
    conn.commit()
    conn.close()

    return success_response("Expense created successfully")


# ===================================
# UPDATE EXPENSE ENDPOINT
# ===================================
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    """
    Update an existing expense by its ID.
    
    URL Parameters:
        expense_id (int): The unique identifier of the expense to update
    
    Expected JSON Request Body:
        {
            "title": "string" (optional),
            "description": "string" (optional),
            "amount": "string" (optional),
            "category": "Food|Education|Entertainment" (optional),
            "user_id": integer (optional)
        }
    
    Returns:
        - HTTP 200: Expense successfully updated
        - HTTP 404: Expense not found
        - HTTP 400: Invalid category
    """
    data = request.get_json()
    
    # Validate category if provided
    category = data.get("category")
    if category and category not in VALID_EXPENSE_CATEGORIES:
        return jsonify({
            "success": False,
            "message": f"Invalid category. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
        }), 400

    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # First, check if the expense exists and get current data
    cursor.execute(SQL_SELECT_EXPENSE_BY_ID, (expense_id,))
    existing_expense = cursor.fetchone()
    
    if not existing_expense:
        conn.close()
        return not_found_response("Expense")

    # Use existing values if new ones aren't provided
    user_id = data.get("user_id", existing_expense["user_id"])
    title = data.get("title", existing_expense["title"])
    amount = data.get("amount", existing_expense["amount"])
    category = data.get("category", existing_expense["category"])
    description = data.get("description", existing_expense["description"])
    date_str = existing_expense["date"]  # Keep original date

    # Update the expense
    cursor.execute(SQL_UPDATE_EXPENSE, (user_id, title, amount, category, date_str, description, expense_id))
    conn.commit()
    conn.close()

    return success_response("Expense updated successfully")


# ===================================
# DELETE EXPENSE ENDPOINT
# ===================================
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    """
    Delete an expense from the system by its ID.
    
    URL Parameters:
        expense_id (int): The unique identifier of the expense to delete
    
    Returns:
        - HTTP 200: Expense successfully deleted
        - HTTP 404: Expense not found
    
    Warning: This operation is irreversible. The expense data will be permanently removed.
    """
    # Connect to database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # First, check if the expense exists
    cursor.execute(SQL_SELECT_EXPENSE_BY_ID, (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return not_found_response("Expense")

    # Expense exists, proceed with deletion
    cursor.execute(SQL_DELETE_EXPENSE, (expense_id,))
    conn.commit()
    conn.close()

    return success_response("Expense deleted successfully")


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
