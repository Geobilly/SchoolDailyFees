from flask import Flask
from flask_cors import CORS

# Import route functions from other modules
from debit_fees import add_fixed_debit
from login import authenticate_user
from student import add_student
from add_fees import add_fee
from fetchdata import get_feeding_fees
from fetchStudent import get_students
from fetch_financial import fetch_financial
from deletestudent import delete_student
from FetchDeletedTransactions import get_deleted_transactions
from DeleteTransaction import delete_transaction
from addImage import upload_image






app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Registering routes with their respective functions
app.route('/add_fixed_debit', methods=['POST'])(add_fixed_debit)
app.route('/authenticate', methods=['POST'])(authenticate_user)
app.route('/add_student', methods=['POST'])(add_student)
app.route('/add_fee', methods=['POST'])(add_fee)
app.route('/feeding_fees', methods=['GET'])(get_feeding_fees)
app.route('/students', methods=['GET'])(get_students)
app.route('/fetch-financial', methods=['POST'])(fetch_financial)
app.route('/delete_student/<string:stu_id>', methods=['DELETE'])(delete_student)
app.route('/deleted_transactions', methods=['GET'])(get_deleted_transactions)
app.route('/delete_transaction', methods=['POST'])(delete_transaction)
app.route('/upload_image', methods=['POST'])(upload_image)




if __name__ == '__main__':
    app.run(debug=True)
