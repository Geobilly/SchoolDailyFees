from flask import Flask
from flask_cors import CORS
from debit_fees import add_fixed_debit
from login import authenticate_user
from student import add_student
from add_fees import add_fee
from fetchdata import get_feeding_fees
from fetchStudent import get_students
from fetch_financial import fetch_financial






app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for all routes



# Registering the login endpoint
app.route('/add_fixed_debit', methods=['POST'])(add_fixed_debit)

# Registering the analyze endpoint
app.route('/authenticate', methods=['POST'])(authenticate_user)

# Registering the Change Password endpoint
app.route('/add_student', methods=['POST'])(add_student)

app.route('/add_fee', methods=['POST'])(add_fee)

app.route('/feeding_fees', methods=['GET'])(get_feeding_fees)

app.route('/students', methods=['GET'])(get_students)

app.route('/fetch-financial', methods=['POST'])(fetch_financial)











if __name__ == '__main__':
    app.run(debug=True)
