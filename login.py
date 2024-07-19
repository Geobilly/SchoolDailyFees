from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import jwt
import datetime

app = Flask(__name__)
CORS(app)

# Secret key for encoding the JWT token
app.config['SECRET_KEY'] = 'your_secret_key'

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Endpoint to authenticate user
@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT username, role FROM user WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                # Generate JWT token
                token = jwt.encode({
                    'username': user['username'],
                    'role': user['role'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expiration time
                }, app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({"username": user['username'], "role": user['role'], "token": token})
            else:
                return jsonify({"error": "Invalid username or password"}), 401
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
