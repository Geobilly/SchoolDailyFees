from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Function to check if a student has been debited within the last 24 hours
def check_debit_within_24hrs(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Define the query to check for debits within the last 24 hours
    query = """
        SELECT * FROM feeding_fees 
        WHERE name = %s AND status = 'debit' AND created_at >= NOW() - INTERVAL 1 DAY
        ORDER BY created_at DESC LIMIT 1
    """
    cursor.execute(query, (name,))
    recent_record = cursor.fetchone()

    cursor.close()
    conn.close()

    return recent_record is not None


# API route to handle the feeding fees process
@app.route('/process_fee', methods=['POST'])
def process_fee():
    # Get data from request
    data = request.json
    name = data['name']
    terminal_price = float(data['terminal_price'])  # Terminal price provided by user

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Fetch the student's ID from the 'student' table
        student_query = "SELECT stu_id FROM student WHERE name = %s"
        cursor.execute(student_query, (name,))
        student_record = cursor.fetchone()

        if not student_record:
            return jsonify({"error": "Student not found"}), 404

        student_id = student_record['stu_id']

        # Step 2: Check if the student has been debited within the last 24 hours
        if check_debit_within_24hrs(name):
            return jsonify({"message": "Student Debited within 24 hours"}), 400

        # Step 3: Get the latest row for the specified name (credit or debit)
        query = """
            SELECT * FROM feeding_fees 
            WHERE name = %s 
            ORDER BY created_at DESC LIMIT 1
        """
        cursor.execute(query, (name,))
        latest_record = cursor.fetchone()

        # If no record is found
        if not latest_record:
            return jsonify({"error": "No record found for this student"}), 404

        # Get the current balance from the latest row
        current_balance = float(latest_record['balance'])

        # Step 4: Check if the balance is sufficient compared to the terminal price
        if current_balance < terminal_price:
            return jsonify({"message": "Low Balance"}), 400

        # Step 5: Deduct the terminal price from the current balance
        new_balance = current_balance - terminal_price

        # Step 6: Insert a new 'debit' record with the updated balance
        insert_query = """
            INSERT INTO feeding_fees (name, class, amount, created_at, status, terminal_id, last_insert, balance, student_id, terminal_name, terminal_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data['name'],
            data['class'],
            -terminal_price,  # Amount is negative for debit
            datetime.now(),  # Created at
            'debit',  # Status
            data['terminal_id'],
            datetime.now(),  # Last insert
            new_balance,  # Updated balance
            student_id,  # Student ID from 'student' table
            data['terminal_name'],
            data['terminal_price']
        ))

        # Commit the transaction
        conn.commit()

        # Return success response
        return jsonify({"message": "Transaction successful", "new_balance": new_balance}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
