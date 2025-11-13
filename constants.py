#-----------------USERS-----------------
SQL_SELECT_ALL_USER = """
SELECT id, username
FROM users;

"""
SQL_SELECT_USER_BY_ID = """
SELECT id, username
FROM users
WHERE id = ?;
"""

SQL_INSERT_USER = """
INSERT INTO users (username, password)
VALUES (?, ?);
"""



SQL_UPDATE_USER = """
UPDATE users
SET username = ?, password = ?
WHERE id = ?;
"""


SQL_DELETE_USER = """
DELETE FROM users
WHERE id = ?;
""" 

#-----------------EXPENSES-----------------
SQL_SELECT_ALL_EXPENSES = """   
SELECT id, user_id, title, amount, category, date, description
FROM expenses;
"""
SQL_SELECT_EXPENSE_BY_ID = """
SELECT id, user_id, title, amount, category, date, description
FROM expenses
WHERE id = ?;
"""
SQL_INSERT_EXPENSE = """    
INSERT INTO expenses (user_id, title, amount, category, date, description)
VALUES (?, ?, ?, ?, ?, ?);
"""

SQL_UPDATE_EXPENSE = """
UPDATE expenses
SET user_id = ?, title = ?, amount = ?, category = ?, date = ?, description = ?
WHERE id = ?;
"""
SQL_DELETE_EXPENSE = """
DELETE FROM expenses
WHERE id = ?;
""" 

# Valid expense categories
VALID_EXPENSE_CATEGORIES = ["Food", "Education", "Entertainment"]

