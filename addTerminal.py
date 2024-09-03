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

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/insert', methods=['POST'])
def insert_terminal():
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    school_id = data.get('school_id')

    if not name or not description or not price or school_id is None:
        return jsonify({'error': 'Missing data'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = connection.cursor()
        query = "INSERT INTO terminal (name, description, price, school_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, description, price, school_id))
        connection.commit()
        cursor.close()
        return jsonify({'message': 'Data inserted successfully'}), 201
    except Error as e:
        print(f"Error inserting data: {e}")
        return jsonify({'error': 'Failed to insert data'}), 500
    finally:
        connection.close()
if __name__ == '__main__':
    app.run(debug=True)
