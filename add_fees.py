from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'srv1241.hstgr.io',
    'user': 'u652725315_dailyfeesuser',
    'password': 'Basic@1998',
    'database': 'u652725315_dialyfees'
}

# Paystack configuration
PAYSTACK_SECRET_KEY = 'sk_live_59bdb4f24d046739292562d30eb55abce7a89b7e'
PAYSTACK_INITIALIZE_URL = 'https://api.paystack.co/transaction/initialize'
PAYSTACK_VERIFY_URL = 'https://api.paystack.co/transaction/verify'


# Helper function to initialize Paystack transaction
def initialize_transaction(amount, mobile_money):
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'amount': int(amount * 100),  # Paystack expects amount in kobo (for NGN) or pesewas (for GHS)
        'email': 'georgeabban79@gmail.com',  # Replace with actual user email
        'currency': 'GHS',
        'phone': mobile_money  # This is optional but useful for verification
    }
    response = requests.post(PAYSTACK_INITIALIZE_URL, headers=headers, json=payload)
    print(f"Initialize Transaction Response: {response.json()}")  # Log for debugging
    if response.status_code == 200:
        return response.json()
    return None


# Helper function to verify Paystack transaction
def verify_transaction(reference):
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
    }
    response = requests.get(f'{PAYSTACK_VERIFY_URL}/{reference}', headers=headers)
    print(f"Verify Transaction Response: {response.json()}")  # Log for debugging
    if response.status_code == 200:
        return response.json()
    return None


# Endpoint to generate payment URL
@app.route('/add_fee', methods=['POST'])
def add_fee():
    data = request.json
    if not isinstance(data, list):
        data = [data]

    responses = []

    for entry in data:
        # Extract necessary fields
        name = entry.get('name')
        student_class = entry.get('class')
        amount = entry.get('amount')
        additional_fees = entry.get('additional_fees', 0)
        status = entry.get('status')
        terminal_id = entry.get('terminal_id')
        terminal_name = entry.get('terminal_name')
        terminal_price = entry.get('terminal_price')
        mobile_money = entry.get('mobile_money')

        # Validate required fields
        if not all([name, student_class, amount, status, terminal_id, terminal_name, terminal_price, mobile_money]):
            responses.append({"error": "All fields are required"})
            continue

        if status != 'credit':
            responses.append({"error": "Invalid status. Must be 'credit'"})
            continue

        # Initiate Paystack transaction
        transaction = initialize_transaction(amount + additional_fees, mobile_money)
        if not transaction or not transaction.get('status'):
            responses.append({"error": "Failed to initialize Paystack transaction"})
            continue

        # Return the payment URL for the front end
        authorization_url = transaction['data']['authorization_url']
        responses.append({"redirect_url": authorization_url, "reference": transaction['data']['reference']})

    return jsonify(responses), 200


# Webhook to handle Paystack payment updates
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    event = payload.get('event')

    print("Webhook received:", payload)  # Log the received payload for debugging

    if event in ['charge.success', 'charge.failed']:
        reference = payload['data']['reference']
        status = payload['data']['status']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Query to fetch student details associated with this reference
            cursor.execute("SELECT * FROM students WHERE reference = %s", (reference,))
            student_data = cursor.fetchone()

            if student_data:
                student_id = student_data[0]
                name = student_data[1]  # Assuming these indices are correct
                student_class = student_data[2]
                amount = student_data[3]
                additional_fees = student_data[4]
                terminal_id = student_data[5]
                terminal_name = student_data[6]
                terminal_price = student_data[7]

                if event == 'charge.success':
                    # Handle successful payment
                    insert_query = """
                        INSERT INTO feeding_fees 
                        (student_id, name, class, amount, additional_fees, status, terminal_id, terminal_name, terminal_price) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                    student_id, name, student_class, amount, additional_fees, 'credit', terminal_id, terminal_name,
                    terminal_price))
                    connection.commit()
                    print("Payment recorded successfully")

                elif event == 'charge.failed':
                    print("Payment failed for reference:", reference)
                    # Handle payment failure (optional)

        except mysql.connector.Error as e:
            print(f"Database error: {e}")

        finally:
            cursor.close()
            connection.close()

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)