from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configure your MySQL connection
db_config = {
    'user': 'your_user',
    'password': 'your_password',
    'host': 'your_host',
    'database': 'your_database'
}

@app.route('/update_amount', methods=['POST'])
def update_amount():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            # Get the data from the request
            data = request.json
            student_id = data['student_id']
            transaction_id = data['transaction_id']
            new_amount = float(data['new_amount'])
            reason = data['reason']

            # Fetch the current amount and balance
            cursor.execute("SELECT amount, balance FROM feeding_fees WHERE id = %s", (transaction_id,))
            record = cursor.fetchone()

            if record:
                old_amount, old_balance = record

                # Calculate the new balance
                new_balance = old_balance - (new_amount - old_amount)

                # Update the amount and balance in feeding_fees
                update_query = """
                UPDATE feeding_fees
                SET amount = %s, balance = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (new_amount, new_balance, transaction_id))

                # Insert the log into editlogss
                log_query = """
                INSERT INTO editlogss (stu_id, name, class, old_amount, new_amount, reason, timestamp)
                SELECT student_id, name, class, %s, %s, %s, NOW()
                FROM feeding_fees
                WHERE id = %s
                """
                cursor.execute(log_query, (old_amount, new_amount, reason, transaction_id))

                # Commit the changes
                connection.commit()

                response = {'status': 'success', 'message': 'Amount and balance updated successfully'}
            else:
                response = {'status': 'error', 'message': 'Transaction ID not found'}

    except Error as e:
        response = {'status': 'error', 'message': str(e)}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
