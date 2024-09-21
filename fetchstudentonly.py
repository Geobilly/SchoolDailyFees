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

# Endpoint to fetch selected student data filtered by school_id
@app.route('/students_only/<string:school_id>', methods=['GET'])
def get_students_only(school_id):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # SQL query to match stu_id starting with the provided school_id
            query = "SELECT stu_id, Name, gender, class FROM student WHERE stu_id LIKE %s"
            like_pattern = f'{school_id}%'  # Create a pattern to match stu_id
            cursor.execute(query, (like_pattern,))
            students = cursor.fetchall()

            return jsonify(students), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
