from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Database connection configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/deleted_transactions', methods=['GET'])
def get_deleted_transactions():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Unable to connect to the database'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM deleted_transactions"
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows)
    except Error as e:
        print(f"Error fetching data from MySQL: {e}")
        return jsonify({'error': 'Error fetching data'}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
