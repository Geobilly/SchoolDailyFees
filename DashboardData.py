from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# Database connection details
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}


def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection


@app.route('/fetch-feeding-fees/<school_id>', methods=['GET'])
def fetch_feeding_fees(school_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch data from the feeding_fees table for the given school_id
        query = """
            SELECT class, amount, status, created_at
            FROM feeding_fees
            WHERE student_id LIKE %s
        """
        cursor.execute(query, (school_id + '%',))
        fees_data = cursor.fetchall()

        # Aggregate total credit and debit for each class
        result = {}
        for record in fees_data:
            class_name = record['class']
            amount = record['amount']
            status = record['status']
            created_at = record['created_at']

            if class_name not in result:
                result[class_name] = {
                    'total_credit': 0,
                    'total_debit': 0,
                    'dates': []
                }

            if status.lower() == 'credit':
                result[class_name]['total_credit'] += amount
            else:
                result[class_name]['total_debit'] += amount

            result[class_name]['dates'].append(created_at)

        return jsonify(result)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
