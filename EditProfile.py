from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# Database connection configuration
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='srv1241.hstgr.io',  # Replace with your database host
            user='u652725315_dailyfeesuser',  # Replace with your database user
            password='Basic@1998',  # Replace with your database password
            database='u652725315_dialyfees'  # Replace with your database name
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/edit_profile/<school_id>', methods=['PUT'])
def edit_profile(school_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"message": "Failed to connect to database"}), 500

    data = request.get_json()

    district = data.get('district')
    region = data.get('region')
    town = data.get('town')
    gps = data.get('gps')
    contact = data.get('contact')
    email = data.get('email')

    if not all([ district, region, town, gps, contact, email]):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        cursor = connection.cursor()
        update_query = """
            UPDATE schools
            SET district = %s, region = %s, town = %s, gps = %s, contact = %s, email = %s
            WHERE school_id = %s
        """
        cursor.execute(update_query, ( district, region, town, gps, contact, email, school_id))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": "School profile updated successfully"}), 200
        else:
            return jsonify({"message": "School ID not found"}), 404

    except Error as e:
        print(f"Error updating profile: {e}")
        return jsonify({"message": "Error updating profile"}), 500

    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
