from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

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


@app.route('/feeding_fees', methods=['GET'])
def get_feeding_fees():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM feeding_fees")
        rows = cursor.fetchall()

        return jsonify(rows)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
