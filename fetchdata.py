from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# MySQL configurations
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Establish a connection to the database
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/feeding_fees/<string:school_id>', methods=['GET'])
def get_feeding_fees(school_id):
    school_id = school_id.strip()  # Remove any leading/trailing whitespace/newline characters

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Query to fetch feeding fees where student_id starts with the given school_id
        query = "SELECT * FROM feeding_fees WHERE student_id LIKE %s"
        cursor.execute(query, (f"{school_id}-%",))
        rows = cursor.fetchall()

        # Debugging: Print the fetched rows
        print(f"Query executed: {query} with school_id: {school_id}")
        print(f"Rows fetched: {rows}")

        return jsonify(rows), 200
    except mysql.connector.Error as err:
        print(f"Error: {str(err)}")  # Debugging statement
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
