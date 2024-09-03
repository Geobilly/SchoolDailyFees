from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS



app = Flask(__name__)
CORS(app)


# Database connection configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


@app.route('/edit_student/<student_id>', methods=['PUT'])
def edit_student(student_id):
    # Retrieve the data from the request
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract the new values from the request data
    name = data.get('Name')
    gender = data.get('gender')
    class_name = data.get('class')

    if not name or not gender or not class_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Connect to the database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Prepare and execute the SQL query
        query = """
            UPDATE student
            SET Name = %s, gender = %s, class = %s
            WHERE stu_id = %s
        """
        values = (name, gender, class_name, student_id)
        cursor.execute(query, values)
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student details updated successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
