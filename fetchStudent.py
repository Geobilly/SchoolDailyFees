from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Function to convert image data to base64 string
def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')

# Endpoint to fetch student data filtered by school_id
@app.route('/students/<string:school_id>', methods=['GET'])
def get_students(school_id):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # SQL query to match stu_id starting with the provided school_id
            query = "SELECT stu_id, Name, gender, class, ProfilePicture FROM student WHERE stu_id LIKE %s"
            like_pattern = f'{school_id}%'  # Create a pattern to match stu_id
            cursor.execute(query, (like_pattern,))
            students = cursor.fetchall()

            # Encode ProfilePicture as base64 string if needed
            for student in students:
                if student['ProfilePicture']:
                    student['ProfilePicture'] = encode_image(student['ProfilePicture'])
                else:
                    student['ProfilePicture'] = None

            return jsonify(students), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
