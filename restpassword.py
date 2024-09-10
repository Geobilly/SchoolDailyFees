from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import random
import string
import requests
from datetime import datetime, timedelta
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host='srv1241.hstgr.io',
        user='u652725315_dailyfeesuser',
        password='Basic@1998',
        database='u652725315_dialyfees'
    )

def generate_code(length=5):
    return ''.join(random.choices(string.digits, k=length))

@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the phone number exists in the schools table
        cursor.execute("SELECT * FROM schools WHERE contact = %s", (phone_number,))
        school = cursor.fetchone()

        if not school:
            return jsonify({'error': 'Phone number not found in the schools table'}), 404

        # Generate a random 5-digit code
        code = generate_code()

        # Save the code to the pass_code table
        cursor.execute("INSERT INTO pass_code (code) VALUES (%s)", (code,))
        connection.commit()

        # Send the code via SMS
        sms_data = {
            "from": "KEMPSHOT",
            "to": phone_number,
            "content": f"Your verification code is: {code}"
        }
        sms_response = requests.post(
            "https://smsc.hubtel.com/v1/messages/send",
            json=sms_data,
            auth=('uppxidtz', 'khhmovbe')
        )

        if sms_response.status_code != 201:
            return jsonify({'error': 'Failed to send SMS'}), 500

        # Schedule the code for deletion after 30 minutes
        expiration_time = datetime.now() + timedelta(minutes=30)
        cursor.execute(
            "UPDATE pass_code SET timestamp = %s WHERE code = %s",
            (expiration_time, code)
        )
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'status': 'success', 'message': 'Verification code sent successfully'}), 200

    except Error as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
