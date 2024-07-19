from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

def generate_student_id():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT MAX(CAST(SUBSTRING(stu_id, 5) AS UNSIGNED)) FROM student WHERE stu_id LIKE 'KGA-%'"
            cursor.execute(query)
            result = cursor.fetchone()
            max_id = result[0] if result[0] else 0
            new_id = f'KGA-{max_id + 1:03d}'
            return new_id
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('Name')
    student_class = data.get('class')
    gender = data.get('gender')

    if not name or not student_class or not gender:
        return jsonify({"error": "Name, class, and gender are required"}), 400

    stu_id = generate_student_id()
    if not stu_id:
        return jsonify({"error": "Failed to generate student ID"}), 500

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO student (stu_id, Name, class, gender) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (stu_id, name, student_class, gender))
            connection.commit()
            return jsonify({"message": "Student added successfully", "stu_id": stu_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
