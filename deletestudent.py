from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/delete_student/<string:stu_id>', methods=['DELETE'])
def delete_student(stu_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = "DELETE FROM student WHERE stu_id = %s"
        cursor.execute(sql, (stu_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'message': 'No student found with the provided ID'}), 404

        return jsonify({'message': f'Student with ID {stu_id} deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
