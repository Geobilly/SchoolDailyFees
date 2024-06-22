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

# Endpoint to fetch student data from the student table
@app.route('/students', methods=['GET'])
def get_students():
    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM student")
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
