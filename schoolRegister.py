from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

## Function to generate school_id
def generate_school_id(school_name):
    # Generate the prefix using the school name's initials
    words = school_name.split()
    initials = ''.join(word[0] for word in words if word)[:3].upper()

    # Query the database to find the highest existing number for this prefix
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT MAX(school_id) FROM schools WHERE school_id LIKE %s"
    like_pattern = f"{initials}-%"
    cursor.execute(query, (like_pattern,))
    result = cursor.fetchone()[0]

    # Extract the last number and increment it
    if result:
        last_number = int(result.split('-')[1])
        new_number = last_number + 1
    else:
        new_number = 1  # Start with 001 if no existing records

    # Format the number with leading zeros
    formatted_number = f"{new_number:03}"

    cursor.close()
    conn.close()

    # Return the new school_id
    return f"{initials}-{formatted_number}"


@app.route('/add_school', methods=['POST'])
def add_school():
    data = request.json
    name = data.get('name')
    region = data.get('region')
    district = data.get('district')
    town = data.get('town')
    gps = data.get('gps')
    contact = data.get('contact')
    email = data.get('email')
    password = data.get('password')

    if not name:
        return jsonify({"error": "School name is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # Generate school ID
    school_id = generate_school_id(name)

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert data into the schools table (without the verification code)
        query = """
        INSERT INTO schools (school_id, name, region, district, town, gps, contact, email, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (school_id, name, region, district, town, gps, contact, email, hashed_password))
        conn.commit()

        return jsonify({"message": "School added successfully", "school_id": school_id}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
