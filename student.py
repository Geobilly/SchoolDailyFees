from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def generate_student_id(school_id):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Adjust query to find the max number for the given school_id
            query = """
                SELECT MAX(CAST(SUBSTRING(stu_id, LENGTH(%s) + 2) AS UNSIGNED))
                FROM student
                WHERE stu_id LIKE %s
            """
            cursor.execute(query, (school_id, f"{school_id}-%"))
            result = cursor.fetchone()
            max_id = result[0] if result[0] else 0
            new_id = f'{school_id}-{max_id + 1:03d}'
            cursor.close()
            connection.close()
            return new_id
    except Error as e:
        print(f"Error generating student ID: {e}")
        return None

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('Name')
    student_class = data.get('class')
    gender = data.get('gender')
    school_id = data.get('school_id')  # Get school_id from request

    if not name or not student_class or not gender or not school_id:
        return jsonify({"error": "Name, class, gender, and school_id are required"}), 400

    stu_id = generate_student_id(school_id)
    if not stu_id:
        return jsonify({"error": "Failed to generate student ID"}), 500

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO student (stu_id, Name, class, gender) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (stu_id, name, student_class, gender))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "Student added successfully", "stu_id": stu_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_student/<string:stu_id>', methods=['DELETE'])
def delete_student(stu_id):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            sql = "DELETE FROM student WHERE stu_id = %s"
            cursor.execute(sql, (stu_id,))
            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({'message': 'No student found with the provided ID'}), 404

            cursor.close()
            connection.close()
            return jsonify({'message': f'Student with ID {stu_id} deleted successfully'}), 200

    except Error as err:
        return jsonify({'error': str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True)
