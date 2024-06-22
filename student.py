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


# Endpoint to insert data into the student table
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('Name')
    student_class = data.get('class')

    if not name or not student_class:
        return jsonify({"error": "Name and class are required"}), 400

    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO student (Name, class) VALUES (%s, %s)"
            cursor.execute(query, (name, student_class))
            connection.commit()
            return jsonify({"message": "Student added successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
