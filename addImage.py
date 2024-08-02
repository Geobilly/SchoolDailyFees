from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL Configuration
mysql_host = 'srv1241.hstgr.io'
mysql_user = 'u652725315_dailyfeesuser'
mysql_password = 'Basic@1998'
mysql_database = 'u652725315_dialyfees'

# Function to establish MySQL connection
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        return conn
    except Error as e:
        print(e)
        return None

# Route to receive POST request with student ID and image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'student_id' not in request.form or 'image' not in request.files:
        return jsonify({'message': 'Missing student_id or image in request'}), 400

    student_id = request.form['student_id']
    image_file = request.files['image']

    # Check if the image file is empty
    if image_file.filename == '':
        return jsonify({'message': 'No image selected for uploading'}), 400

    try:
        # Connect to MySQL
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'message': 'Database connection error'}), 500

        cursor = connection.cursor()

        # Check if student_id exists
        cursor.execute("SELECT * FROM student WHERE stu_id = %s", (student_id,))
        student = cursor.fetchone()

        if student is None:
            return jsonify({'message': 'Student not found'}), 404

        # Read image data from file
        image_data = image_file.read()

        # Update student record with image data
        update_query = """
        UPDATE student
        SET ProfilePicture = %s
        WHERE stu_id = %s
        """
        cursor.execute(update_query, (image_data, student_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': 'Image uploaded successfully'}), 200

    except Error as e:
        print(e)
        return jsonify({'message': 'Error uploading image to database'}), 500

# Route to retrieve image data
@app.route('/get_image/<student_id>', methods=['GET'])
def get_image(student_id):
    try:
        # Connect to MySQL
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'message': 'Database connection error'}), 500

        cursor = connection.cursor()

        # Fetch image data
        cursor.execute("SELECT ProfilePicture FROM student WHERE stu_id = %s", (student_id,))
        image_data = cursor.fetchone()

        if image_data is None:
            return jsonify({'message': 'Student not found or no image available'}), 404

        # Set response headers
        response = app.response_class(
            response=image_data[0],
            status=200,
            mimetype='image/jpeg'  # Adjust mimetype according to the image format
        )

        cursor.close()
        connection.close()

        return response

    except Error as e:
        print(e)
        return jsonify({'message': 'Error retrieving image from database'}), 500

if __name__ == '__main__':
    app.run(debug=True)
