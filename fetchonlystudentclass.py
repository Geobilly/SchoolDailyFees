from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Endpoint to fetch selected student data filtered by school_id and class
@app.route('/students_only/<string:school_id>/<string:student_class>', methods=['GET'])
def get_students_only(school_id, student_class):
    try:
        # Establish MySQL connection
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Trim spaces from student_class
            student_class = student_class.strip()

            # Debug print to check input parameters
            print(f"Executing query with school_id='{school_id}', class='{student_class}'")

            # SQL query to match stu_id starting with the provided school_id and specific class
            query = "SELECT stu_id, Name, gender, class FROM student WHERE stu_id LIKE %s AND class = %s"
            like_pattern = f'{school_id}%'  # Create a pattern to match stu_id

            # Execute query with parameters
            cursor.execute(query, (like_pattern, student_class))
            students = cursor.fetchall()

            # Debug print to check fetched students
            print(f"Fetched students: {students}")

            # Return the result as JSON
            return jsonify(students), 200

    except Error as e:
        # Debug print to catch any database errors
        print(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
