import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from requests.auth import HTTPBasicAuth

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

# Hubtel API credentials
HUBTEL_CLIENT_ID = 'uppxidtz'
HUBTEL_CLIENT_SECRET = 'khhmovbe'
HUBTEL_API_URL = 'https://smsc.hubtel.com/v1/messages/send'

# Route for creating a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    gender = data.get('gender')
    role = data.get('role')
    email = data.get('email')
    contact = data.get('contact')
    password = data.get('password')
    school_id = data.get('school_id')
    user_class = data.get('class')  # Extract the 'class' parameter


    # Hash the password
    hashed_password = generate_password_hash(password)

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to insert data
        sql = """INSERT INTO usersrole (name, gender, role, email, contact, password, school_id, class) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (name, gender, role, email, contact, hashed_password, school_id, user_class,))

        # Commit the transaction
        conn.commit()

        # Prepare SMS payload
        sms_data = {
            'from': 'KEMPSHOT',  # Must be 11 alpha-numeric characters or less; subject to approval by Hubtel.
            'to': contact,  # Recipient's telephone number in E164 format
            'content': f'Welcome {name}, your email is {email} and your password is {password}.'
        }

        # Send SMS request
        sms_response = requests.post(
            HUBTEL_API_URL,
            json=sms_data,
            auth=HTTPBasicAuth(HUBTEL_CLIENT_ID, HUBTEL_CLIENT_SECRET)
        )

        if sms_response.status_code != 200:
            print("Error sending SMS:", sms_response.text)

        response = {
            'message': 'User added successfully!'
        }

        cursor.close()
        conn.close()
        return jsonify(response), 201

    except Error as e:
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
