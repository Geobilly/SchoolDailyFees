from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
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
    return mysql.connector.connect(**db_config)


@app.route('/fetch-financial/<school_id>', methods=['POST'])
def fetch_financial(school_id):
    try:
        data = request.json
        date = data['date']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all student names and classes for the given school_id
        cursor.execute("""
            SELECT Name, class
            FROM student
            WHERE stu_id LIKE %s
        """, (f"{school_id}-%",))
        student_data = cursor.fetchall()

        # Create a dictionary to map students to their classes
        student_classes = {student['Name']: student['class'] for student in student_data}

        # Fetch feeding fee data for the date
        cursor.execute("""
            SELECT name, class, amount
            FROM feeding_fees
            WHERE DATE(created_at) = %s AND status = 'debit' AND student_id LIKE %s
        """, (date, f"{school_id}-%"))
        debited_records = cursor.fetchall()

        # Initialize dict to store debited amounts per student
        debited_amounts = {name: 0.0 for name in student_classes.keys()}

        # Sum up debited amounts per student
        for record in debited_records:
            student_name = record['name']
            amount = float(record['amount'])
            debited_amounts[student_name] += amount

        # Initialize dict to store not debited amounts per class
        not_debited_amounts = {class_name: 0.0 for class_name in set(student_classes.values())}
        not_debited_students = {class_name: [] for class_name in set(student_classes.values())}

        # Calculate not debited amounts and count not debited students per class
        for name, total_amount in debited_amounts.items():
            if total_amount == 0.0:
                class_name = student_classes[name]
                # Calculate not debited amount based on total number of students in the class
                total_students_in_class = sum(
                    1 for student_class in student_classes.values() if student_class == class_name)
                not_debited_amounts[class_name] += total_students_in_class
                not_debited_students[class_name].append(name)

        # Fetch total number of students for each class
        cursor.execute("""
            SELECT class, COUNT(*) as total_students
            FROM student
            WHERE stu_id LIKE %s
            GROUP BY class
        """, (f"{school_id}-%",))
        student_summary = cursor.fetchall()

        # Fetch feeding fee data (corrected table name)
        cursor.execute("""
            SELECT class,
                   SUM(CASE WHEN status = 'credit' THEN amount ELSE 0 END) as total_credit,
                   SUM(CASE WHEN status = 'debit' THEN amount ELSE 0 END) as total_debit,
                   COUNT(CASE WHEN status = 'debit' THEN 1 ELSE NULL END) as count_debit
            FROM feeding_fees
            WHERE DATE(created_at) = %s AND student_id LIKE %s
            GROUP BY class
        """, (date, f"{school_id}-%"))
        feeding_summary = cursor.fetchall()

        # Combine student_summary with feeding_summary based on class
        combined_summary = []
        for student_data in student_summary:
            class_name = student_data['class']
            total_not_debited = not_debited_amounts.get(class_name, 0.0)
            not_debited_count = len(not_debited_students.get(class_name, []))
            for feeding_data in feeding_summary:
                if feeding_data['class'].lower() == class_name.lower():
                    combined_summary.append({
                        'class': class_name,
                        'total_students': student_data['total_students'],
                        'total_credit': feeding_data['total_credit'],
                        'total_debit': feeding_data['total_debit'],
                        'count_debit': feeding_data['count_debit'],
                        'total_not_debited': total_not_debited,
                        'num_not_debited_students': not_debited_count
                    })
                    break
            else:
                # Add student_summary entries without matching feeding_summary data
                combined_summary.append({
                    'class': class_name,
                    'total_students': student_data['total_students'],
                    'total_credit': "0.00",
                    'total_debit': "0.00",
                    'count_debit': 0,
                    'total_not_debited': total_not_debited,
                    'num_not_debited_students': not_debited_count
                })

        cursor.close()
        connection.close()

        return jsonify({
            'combined_summary': combined_summary,
            'not_debited_students': not_debited_students  # Optionally include not debited students separately
        })

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
