from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Route for user login
@app.route('/userlogin', methods=['POST'])
def userrlogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to check if user exists
        cursor.execute("SELECT * FROM usersrole WHERE email = %s", (email,))
        user = cursor.fetchone()

        # If user exists and password matches
        if user and check_password_hash(user['password'], password):
            response = {
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'gender': user['gender'],
                    'role': user['role'],
                    'email': user['email'],
                    'contact': user['contact'],
                    'school_id': user['school_id'],
                    'class': user['class']

                }
            }
            status_code = 200
        else:
            response = {'message': 'Invalid email or password'}
            status_code = 401

        cursor.close()
        conn.close()
        return jsonify(response), status_code

    except Error as e:
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
