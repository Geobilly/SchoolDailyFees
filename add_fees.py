
from flask import Flask, request, jsonify
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

# Endpoint to insert data into the feeding_fees table
@app.route('/add_fee', methods=['POST'])
def add_fee():
    data = request.json

    if not isinstance(data, list):
        data = [data]

    responses = []

    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            for entry in data:
                name = entry.get('name')
                student_class = entry.get('class')
                amount = entry.get('amount')
                status = entry.get('status')
                terminal_id = entry.get('terminal_id')
                terminal_name = entry.get('terminal_name')
                terminal_price = entry.get('terminal_price')

                if not name or not student_class or not amount or not status or not terminal_id or not terminal_name or terminal_price is None:
                    responses.append({"error": "Name, class, amount, status, terminal_id, terminal_name, and terminal_price are required"})
                    continue

                if status != 'credit':
                    responses.append({"error": "Invalid status. Must be 'credit'"})
                    continue

                # Retrieve student_id from the student table
                select_student_query = """
                    SELECT stu_id
                    FROM student
                    WHERE name = %s AND class = %s
                """
                cursor.execute(select_student_query, (name, student_class))
                student = cursor.fetchone()

                if not student:
                    responses.append({"error": f"Student not found for {name} in class {student_class}"})
                    continue

                student_id = student['stu_id']
                print(f"Retrieved student_id: {student_id}")  # Debugging line

                # Insert new data
                insert_query = """
                    INSERT INTO feeding_fees (student_id, name, class, amount, status, terminal_id, terminal_name, terminal_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    cursor.execute(insert_query, (student_id, name, student_class, amount, status, terminal_id, terminal_name, terminal_price))
                    connection.commit()

                    # Get the last inserted ID
                    last_id = cursor.lastrowid

                    # Calculate the new balance for this student
                    select_query = """
                        SELECT SUM(amount) as total_amount
                        FROM feeding_fees
                        WHERE student_id = %s
                    """
                    cursor.execute(select_query, (student_id,))
                    result = cursor.fetchone()
                    total_amount = result['total_amount'] if result else 0

                    # Update the balance column for this row
                    update_query = """
                        UPDATE feeding_fees
                        SET balance = %s
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (total_amount, last_id))
                    connection.commit()

                    responses.append({"message": "Fees Added Successfully"})

                except mysql.connector.Error as insert_err:
                    print(f"Insert error: {insert_err}")  # Debugging line
                    responses.append({"error": str(insert_err)})

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return jsonify(responses), 201

if __name__ == '__main__':
    app.run(debug=True)  