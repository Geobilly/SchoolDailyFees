from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from decimal import Decimal
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


# Function to retrieve student_id from student table
def get_student_id(name, student_class):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        select_query = "SELECT stu_id FROM student WHERE name = %s AND class = %s"
        cursor.execute(select_query, (name, student_class))
        result = cursor.fetchone()
        return result['stu_id'] if result else None
    except Error as e:
        print(f"Error retrieving student_id: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Function to retrieve current balance for a specific terminal
def get_terminal_balance(terminal_name, terminal_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        select_query = "SELECT balance FROM feeding_fees WHERE terminal_name = %s AND terminal_id = %s ORDER BY created_at DESC LIMIT 1"
        cursor.execute(select_query, (terminal_name, terminal_id))
        result = cursor.fetchone()
        return Decimal(result['balance']) if result and result['balance'] is not None else Decimal('0.00')
    except Error as e:
        print(f"Error retrieving terminal balance: {e}")
        return Decimal('0.00')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Function to check if a debit entry exists for a specific student within the last 24 hours
def has_debited_last_24_hours(student_id, terminal_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        select_query = """
            SELECT COUNT(*) as count FROM feeding_fees 
            WHERE student_id = %s AND terminal_id = %s AND status = 'debit' 
            AND created_at >= %s
        """
        last_24_hours = datetime.now() - timedelta(hours=24)
        cursor.execute(select_query, (student_id, terminal_id, last_24_hours))
        result = cursor.fetchone()
        return result['count'] > 0
    except Error as e:
        print(f"Error checking debits in last 24 hours: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/add_fixed_debit', methods=['POST'])
def add_fixed_debit():
    data = request.json
    name = data.get('name')
    student_class = data.get('class')
    terminal_id = data.get('terminal_id')
    terminal_name = data.get('terminal_name')
    terminal_price = Decimal(data.get('terminal_price'))

    if not name or not student_class or not terminal_id or not terminal_name or terminal_price is None:
        return jsonify({"error": "Name, class, terminal_id, terminal_name, and terminal_price are required"}), 400

    amount = -terminal_price
    status = 'debit'

    # Get student_id based on name and class
    student_id = get_student_id(name, student_class)
    if student_id is None:
        return jsonify({"error": "Student not found"}), 404

    # Check if student has debited within the last 24 hours
    if has_debited_last_24_hours(student_id, terminal_id):
        return jsonify({"error": "Student has already been debited in the last 24 hours"}), 400

    # Get current balance for the terminal
    terminal_balance = get_terminal_balance(terminal_name, terminal_id)
    if terminal_balance < terminal_price:
        return jsonify({"error": "Not enough balance"}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Insert new data with fixed debit value
            insert_query = """
                INSERT INTO feeding_fees (name, class, amount, status, student_id, terminal_id, terminal_name, terminal_price, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                name, student_class, amount, status, student_id, terminal_id, terminal_name, terminal_price,
                datetime.now()
            ))
            connection.commit()

            # Get the last inserted ID
            last_id = cursor.lastrowid

            # Calculate the new balance for this terminal
            new_terminal_balance = terminal_balance + amount

            # Update the balance column for this row
            update_query = "UPDATE feeding_fees SET balance = %s WHERE id = %s"
            cursor.execute(update_query, (new_terminal_balance, last_id))
            connection.commit()

            return jsonify({"message": "Fees Debited and balance updated successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)