from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
from io import StringIO

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


# Connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/bulk-upload', methods=['POST'])
def bulk_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File is not a CSV'}), 400

    try:
        # Read CSV file
        data = pd.read_csv(file)

        # Ensure required columns are present
        required_columns = ['stu_id', 'Name', 'gender', 'class']
        if not all(column in data.columns for column in required_columns):
            return jsonify({'error': 'Missing required columns'}), 400

        # Insert data into the database
        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in data.iterrows():
            cursor.execute("""
                INSERT INTO student (stu_id, Name, gender, class)
                VALUES (%s, %s, %s, %s)
            """, (row['stu_id'], row['Name'], row['gender'], row['class']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
