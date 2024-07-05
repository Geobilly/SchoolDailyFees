from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error: '{e}'")
    return connection

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    data = request.json
    date = data.get('date')  # Get the date from the POST request

    if not date:
        return jsonify({'error': 'Date is required'}), 400

    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch all students
            cursor.execute("SELECT * FROM student")
            students = cursor.fetchall()
            print(f"Students: {students}")  # Debugging statement

            # Check the keys in the first student record (if exists)
            if students:
                print(f"Student record keys: {students[0].keys()}")

            # Using 'stu_id' as the primary key column in the student table
            student_ids = [student['stu_id'] for student in students]

            # Fetch feeding_fees records for the given date
            query = """
                SELECT * FROM feeding_fees
                WHERE DATE(created_at) = %s AND status = 'debit'
            """
            cursor.execute(query, (date,))
            feeding_fees = cursor.fetchall()
            print(f"Feeding Fees: {feeding_fees}")  # Debugging statement

            # Filter out students who have feeding_fees records
            feeding_student_ids = {fee['student_id'] for fee in feeding_fees}
            filtered_students = [student for student in students if student['stu_id'] not in feeding_student_ids]

            return jsonify(filtered_students), 200

    except Error as e:
        print(f"Error: '{e}'")
        return jsonify({'error': str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
