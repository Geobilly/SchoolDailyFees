from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host='srv1241.hstgr.io',
        user='u652725315_dailyfeesuser',
        password='Basic@1998',
        database='u652725315_dialyfees'
    )

@app.route('/delete_transaction', methods=['POST'])
def delete_transaction():
    data = request.get_json()

    transaction_id = data.get('id')
    reason = data.get('reason')

    if not all([transaction_id, reason]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get the data of the row to be deleted
        cursor.execute("SELECT id, name, class, amount, created_at, status, last_insert, balance, student_id, terminal_id FROM feeding_fees WHERE id = %s", (transaction_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'error': 'Transaction not found'}), 404

        # Prepare the data for insertion into the deleted_transactions table
        id, name, class_, amount, created_at, status, last_insert, balance, student_id, terminal_id = row
        deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert the row data into deleted_transactions table
        insert_query = """
        INSERT INTO deleted_transactions (id, name, class, amount, created_at, status, last_insert, balance, student_id, reason, deleted_at, terminal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (id, name, class_, amount, created_at, status, last_insert, balance, student_id, reason, deleted_at, terminal_id))

        # Delete the row from feeding_fees table
        delete_query = "DELETE FROM feeding_fees WHERE id = %s"
        cursor.execute(delete_query, (transaction_id,))

        # Commit changes
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success'}), 200

    except Error as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
