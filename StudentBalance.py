from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

@app.route('/get_balance/<school_id>', methods=['POST'])
def get_balance(school_id):
    data = request.get_json()
    class_name = data.get('Class')
    terminal_name = data.get('Terminal')
    student_name = data.get('Name')

    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # If student_name is provided, get only that student's info, otherwise get all students in the specified class
        if student_name:
            # Fetch the student with the specified name and school_id
            query = "SELECT stu_id, Name, class FROM student WHERE Name = %s AND stu_id LIKE %s"
            cursor.execute(query, (student_name, f"{school_id}%"))
        else:
            # Fetch all students in the specified class and school_id
            query = "SELECT stu_id, Name, class FROM student WHERE class = %s AND stu_id LIKE %s"
            cursor.execute(query, (class_name, f"{school_id}%"))

        students = cursor.fetchall()

        # If no students found, return an empty list with a balance of 0 for the specified class or name
        if not students:
            return jsonify([{'name': student_name if student_name else 'No student found', 'balance': 0, 'class': class_name, 'stu_id': 'N/A'}])

        # Prepare the response with balances
        balances = []
        for student in students:
            # Query to get the latest balance for each student in the specified terminal
            balance_query = """
            SELECT balance FROM feeding_fees
            WHERE name = %s AND terminal_name = %s
            ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(balance_query, (student['Name'], terminal_name))
            balance_result = cursor.fetchone()

            # If no balance record found, set balance to 0
            balance = balance_result['balance'] if balance_result else 0
            balances.append({
                'stu_id': student['stu_id'],
                'name': student['Name'],
                'class': student['class'],
                'balance': balance
            })

        return jsonify(balances)

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
