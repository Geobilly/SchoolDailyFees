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

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_terminal(id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = connection.cursor()
        query = "DELETE FROM terminal WHERE id = %s"
        cursor.execute(query, (id,))
        connection.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No record found with the given ID'}), 404

        return jsonify({'message': 'Data deleted successfully'}), 200
    except Error as e:
        print(f"Error deleting data: {e}")
        return jsonify({'error': 'Failed to delete data'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
