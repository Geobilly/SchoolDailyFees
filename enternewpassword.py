from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
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


# Establish a database connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection


# Route for validating code and updating password
@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        phone_number = data['phone_number']
        code = data['code']
        new_password = data['password']

        # Establish a database connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if the entered code matches any code in the pass_code table
        query_code = "SELECT * FROM pass_code WHERE code = %s"
        cursor.execute(query_code, (code,))
        code_row = cursor.fetchone()

        if code_row:
            # Check if phone number exists in the schools table
            query_school = "SELECT * FROM schools WHERE contact = %s"
            cursor.execute(query_school, (phone_number,))
            school_row = cursor.fetchone()

            if school_row:
                # Hash the new password
                hashed_password = generate_password_hash(new_password)

                # Update the password in the schools table
                update_query = "UPDATE schools SET password = %s WHERE contact = %s"
                cursor.execute(update_query, (hashed_password, phone_number))
                connection.commit()

                return jsonify({"message": "Password updated successfully.", "status": "success"}), 200
            else:
                return jsonify({"message": "Phone number not found.", "status": "error"}), 404
        else:
            return jsonify({"message": "Invalid code.", "status": "error"}), 400

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
