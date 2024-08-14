from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
import random
import requests
import base64
from flask_cors import CORS



app = Flask(__name__)
CORS(app)


# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# # Hubtel API Configuration
# HUBTEL_CLIENT_ID = 'uppxidtz'
# HUBTEL_CLIENT_SECRET = 'khhmovbe'
# HUBTEL_FROM = 'KEMPSHOT'  # Ensure this is 11 characters or less and approved by Hubtel
# HUBTEL_API_URL = 'https://smsc.hubtel.com/v1/messages/send'

## Function to generate school_id
def generate_school_id(school_name):
    # Generate the prefix using the school name's initials
    words = school_name.split()
    initials = ''.join(word[0] for word in words if word)[:3].upper()

    # Query the database to find the highest existing number for this prefix
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT MAX(school_id) FROM schools WHERE school_id LIKE %s"
    like_pattern = f"{initials}-%"
    cursor.execute(query, (like_pattern,))
    result = cursor.fetchone()[0]

    # Extract the last number and increment it
    if result:
        last_number = int(result.split('-')[1])
        new_number = last_number + 1
    else:
        new_number = 1  # Start with 001 if no existing records

    # Format the number with leading zeros
    formatted_number = f"{new_number:03}"

    cursor.close()
    conn.close()

    # Return the new school_id
    return f"{initials}-{formatted_number}"


# # Function to generate a random 6-digit verification code
# def generate_verification_code():
#     return str(random.randint(100000, 999999))

# # Function to send SMS via Hubtel
# def send_sms(contact, verification_code):
#     # Prepare the basic auth header
#     auth_credentials = f"{HUBTEL_CLIENT_ID}:{HUBTEL_CLIENT_SECRET}"
#     auth_header = base64.b64encode(auth_credentials.encode()).decode()
#
#     # Prepare the request headers and body
#     headers = {
#         'Authorization': f'Basic {auth_header}',
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         "from": HUBTEL_FROM,
#         "to": contact,
#         "content": f'Your verification code is {verification_code}'
#     }
#
#     # Send the request
#     response = requests.post(HUBTEL_API_URL, json=payload, headers=headers)
#     return response.status_code, response.json()

@app.route('/add_school', methods=['POST'])
def add_school():
    data = request.json
    name = data.get('name')
    region = data.get('region')
    district = data.get('district')
    town = data.get('town')
    gps = data.get('gps')
    contact = data.get('contact')
    email = data.get('email')
    password = data.get('password')

    if not name:
        return jsonify({"error": "School name is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # # Generate school ID and verification code
    # school_id = generate_school_id(name)
    # verification_code = generate_verification_code()

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert data into the schools table, including the verification code
        query = """
        INSERT INTO schools (school_id, name, region, district, town, gps, contact, email, password, authentication)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s)
        """
        cursor.execute(query, (school_id, name, region, district, town, gps, contact, email, hashed_password, verification_code))
        conn.commit()

        # Send the verification code via SMS
        status_code, response_json = send_sms(contact, verification_code)
        if status_code == 200 or status_code == 201:
            return jsonify({"message": "School added successfully", "school_id": school_id}), 201
        else:
            return jsonify({"error": f"Failed to send SMS: {response_json}"}), 500

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
