from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Database connection details
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Function to get database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# API to get student count and total credit/debit for a given school_id
@app.route('/school/<school_id>', methods=['GET'])
def get_school_data(school_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get the total number of students for the given school_id
        student_query = """
        SELECT COUNT(*) AS total_students
        FROM student
        WHERE stu_id LIKE %s
        """
        cursor.execute(student_query, (school_id + '%',))
        student_count = cursor.fetchone()['total_students']

        # Get total credit and debit from the feeding_fees table for the given school_id
        fees_query = """
        SELECT 
            SUM(CASE WHEN status = 'credit' THEN amount ELSE 0 END) AS total_credit,
            SUM(CASE WHEN status = 'debit' THEN amount ELSE 0 END) AS total_debit
        FROM feeding_fees
        WHERE student_id LIKE %s
        """
        cursor.execute(fees_query, (school_id + '%',))
        fees_data = cursor.fetchone()

        response = {
            'school_id': school_id,
            'total_students': student_count,
            'total_credit': fees_data['total_credit'] or 0.0,
            'total_debit': fees_data['total_debit'] or 0.0
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
