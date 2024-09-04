from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# MySQL database connection configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


# Function to establish a connection to the database
def get_db_connection():
    connection = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    return connection


# API route to fetch data for a specific school_id from the schools table
@app.route('/get_school/<string:school_id>', methods=['GET'])
def get_school(school_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT name, district, region, town, gps, contact, email FROM schools WHERE school_id = %s"
        cursor.execute(query, (school_id,))

        # Fetch the row corresponding to the provided school_id
        school = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        if school:
            return jsonify(school)
        else:
            return jsonify({"error": "School not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


if __name__ == '__main__':
    app.run(debug=True)
