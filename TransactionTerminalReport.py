from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection details
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Function to get database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# API to get feeding fees data for a given school_id
@app.route('/school_transactions/<school_id>', methods=['GET'])
def get_feeding_fees(school_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the necessary fields from feeding_fees table filtered by school_id
        fees_query = """
        SELECT 
            id, 
            name, 
            class, 
            amount, 
            created_at, 
            status, 
            terminal_id, 
            last_insert, 
            balance, 
            student_id, 
            terminal_name, 
            terminal_price
        FROM feeding_fees
        WHERE student_id LIKE %s
        """
        print(f'Executing query: {fees_query} with school_id: {school_id}')
        cursor.execute(fees_query, ('%' + school_id + '%',))  # Match anywhere in the student_id
        fees_data = cursor.fetchall()
        print(f'Fees data retrieved: {fees_data}')

        # If data is found, return it; else return a message
        if fees_data:
            return jsonify({'feeding_fees': fees_data})
        else:
            return jsonify({'message': f'No feeding fees data found for school_id {school_id}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
