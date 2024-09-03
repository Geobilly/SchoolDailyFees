from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Endpoint to fetch data from the terminal table based on school_id
@app.route('/get_terminal/<school_id>', methods=['GET'])
def get_terminal(school_id):
    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            select_query = """
                SELECT id, name, description, price, school_id, timestamp
                FROM terminal
                WHERE school_id = %s
            """
            cursor.execute(select_query, (school_id,))
            results = cursor.fetchall()

            if results:
                return jsonify(results), 200
            else:
                return jsonify({"error": "No terminals found for the provided school_id"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
