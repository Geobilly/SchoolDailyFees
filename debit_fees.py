from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error

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

        select_query = """
            SELECT stu_id
            FROM student
            WHERE name = %s AND class = %s
        """
        cursor.execute(select_query, (name, student_class))
        result = cursor.fetchone()

        if result:
            return result['stu_id']
        else:
            return None

    except Error as e:
        print(f"Error retrieving student_id: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to retrieve current balance for a student
def get_current_balance(name, student_class):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        select_query = """
            SELECT SUM(amount) as total_amount
            FROM feeding_fees
            WHERE name = %s AND class = %s
        """
        cursor.execute(select_query, (name, student_class))
        result = cursor.fetchone()

        if result:
            return result['total_amount'] if result['total_amount'] is not None else 0
        else:
            return 0

    except Error as e:
        print(f"Error retrieving current balance: {e}")
        return 0

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Endpoint to insert data into the feeding_fees table with a fixed debit value of -8.00
@app.route('/add_fixed_debit', methods=['POST'])
def add_fixed_debit():
    data = request.json
    name = data.get('name')
    student_class = data.get('class')

    if not name or not student_class:
        return jsonify({"error": "Name and class are required"}), 400

    amount = -8.00
    status = 'debit'

    # Get student_id based on name and class
    student_id = get_student_id(name, student_class)
    if student_id is None:
        return jsonify({"error": "Student not found"}), 404

    # Get current balance for the student
    current_balance = get_current_balance(name, student_class)
    if current_balance < 8:
        return jsonify({"error": "Not enough balance"}), 400

    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Insert new data with fixed debit value
            insert_query = """
                INSERT INTO feeding_fees (name, class, amount, status, student_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, student_class, amount, status, student_id))
            connection.commit()

            # Get the last inserted ID
            last_id = cursor.lastrowid

            # Calculate the new balance for this student
            total_amount = current_balance + amount

            # Update the balance column for this row
            update_query = """
                UPDATE feeding_fees
                SET balance = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (total_amount, last_id))
            connection.commit()

            return jsonify({"message": "Fee added and balance updated successfully"}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
