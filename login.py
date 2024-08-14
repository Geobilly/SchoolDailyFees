from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash
import jwt
import datetime
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

# Secret key for encoding the JWT
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Database connection details
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


# Function to generate JWT token
def generate_token(user):
    token = jwt.encode({
        'school_id': user['school_id'],
        'name': user['name'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return token


# Login API route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        with conn.cursor(dictionary=True) as cursor:
            # Query to find the user by email
            query = "SELECT school_id, name, password FROM schools WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                # Authentication successful
                token = generate_token(user)
                return jsonify({
                    'message': 'Login successful',
                    'school_id': user['school_id'],
                    'name': user['name'],
                    'token': token
                }), 200
            else:
                # Authentication failed
                return jsonify({'message': 'Invalid email or password'}), 401

    except mysql.connector.Error as err:
        # Handle database connection errors
        return jsonify({'message': 'Database connection failed', 'error': str(err)}), 500

    finally:
        if conn:
            conn.close()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
