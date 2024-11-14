from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime, timedelta

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# POST API to add or update attendance record
@app.route('/attendance', methods=['POST'])
def add_attendance():
    data = request.json
    stu_id = data.get('stu_id')
    student_name = data.get('student_name')
    status = data.get('status')

    # Use today's date if attendance_date is not provided
    attendance_date = date.today()

    # Check if required fields are provided
    if not all([stu_id, student_name, status]):
        return jsonify({'error': 'Missing fields in request'}), 400

    try:
        # Establish a connection to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if a record already exists for this stu_id and attendance_date
        query_check = """
            SELECT attendance_date, attendance_time FROM attendancee
            WHERE stu_id = %s AND attendance_date = %s
        """
        cursor.execute(query_check, (stu_id, attendance_date))
        existing_record = cursor.fetchone()

        current_time = datetime.now().time()

        if existing_record:
            # If a record exists, calculate the time difference
            existing_date, existing_time = existing_record

            # Check if existing_time is a timedelta and convert it to time if necessary
            if isinstance(existing_time, timedelta):
                existing_time = (datetime.min + existing_time).time()

            existing_datetime = datetime.combine(existing_date, existing_time)
            current_datetime = datetime.combine(attendance_date, current_time)

            # If the record is within 24 hours, update it
            if (current_datetime - existing_datetime) <= timedelta(hours=24):
                query_update = """
                    UPDATE attendancee
                    SET student_name = %s, status = %s, attendance_time = %s
                    WHERE stu_id = %s AND attendance_date = %s
                """
                cursor.execute(query_update, (student_name, status, current_time, stu_id, attendance_date))
                conn.commit()
                return jsonify({'message': 'Attendance record updated successfully'}), 200
            else:
                # If the record is older than 24 hours, insert a new record
                query_insert = """
                    INSERT INTO attendancee (stu_id, student_name, attendance_date, attendance_time, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query_insert, (stu_id, student_name, attendance_date, current_time, status))
                conn.commit()
                return jsonify({'message': 'New attendance record added successfully'}), 201
        else:
            # If no record exists, insert a new record
            query_insert = """
                INSERT INTO attendancee (stu_id, student_name, attendance_date, attendance_time, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, (stu_id, student_name, attendance_date, current_time, status))
            conn.commit()
            return jsonify({'message': 'New attendance record added successfully'}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to add or update attendance record'}), 500

    finally:
        # Close the database connection
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
