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

@app.route('/edit/<int:id>', methods=['PUT'])
def edit_terminal(id):
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    if name is None and description is None and price is None:
        return jsonify({'error': 'No data to update'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = connection.cursor()
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if price is not None:
            updates.append("price = %s")
            params.append(price)

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        updates_str = ", ".join(updates)
        query = f"UPDATE terminal SET {updates_str} WHERE id = %s"
        params.append(id)

        cursor.execute(query, tuple(params))
        connection.commit()
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No record found with the given ID'}), 404

        return jsonify({'message': 'Data updated successfully'}), 200
    except Error as e:
        print(f"Error updating data: {e}")
        return jsonify({'error': 'Failed to update data'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
