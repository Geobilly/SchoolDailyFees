from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
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


# Function to create a connection to the database
def create_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


# Route to handle the posting of staff data
@app.route('/staff', methods=['POST'])
def add_staff():
    try:
        # Extract data from the request
        data = request.json
        school_id = data.get('school_id')
        role = data.get('role')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        gender = data.get('gender')
        contact = data.get('contact')

        # Validate required fields
        if not all([school_id, role, first_name, last_name, email, gender, contact]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Connect to the database
        connection = create_db_connection()
        if connection is None:
            return jsonify({'message': 'Database connection failed'}), 500

        # SQL query to insert data
        insert_query = """
            INSERT INTO staff (school_id, role, firstName, lastName, email, gender, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (school_id, role, first_name, last_name, email, gender, contact)

        # Execute the query
        cursor = connection.cursor()
        cursor.execute(insert_query, values)
        connection.commit()

        # Close the connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'User added successfully'}), 201

    except Exception as e:
        return jsonify({'message': f'An error occurred: {e}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
