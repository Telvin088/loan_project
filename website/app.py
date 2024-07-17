from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import requests
import base64
from flask_mail import Mail, Message
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="loan_auth"
)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'loan_auth'
}

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='loan_auth'
    )

UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'telvinngichukii@gmail.com'
app.config['MAIL_PASSWORD'] = 'pgnt fflh cyub jssn'

mail = Mail(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="loan_auth"
    )


@app.route('/submit_loan_application', methods=['POST'])
def submit_loan_application():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        session_id = request.form['session_id']
        loan_type = request.form['loan_type']
        amount = float(request.form['amount'])  # Convert to float for decimal handling

        # Connect to MySQL
        connection = create_connection()
        cursor = connection.cursor()

        # Insert data into the loan_applications table
        insert_query = """
        INSERT INTO loan_applications (username, email, session_id, loan_type, amount)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (username, email, session_id, loan_type, amount)
        cursor.execute(insert_query, data)

        # Commit changes and close connection
        connection.commit()
        cursor.close()
        connection.close()

        # Redirect to a success page or home page
        return redirect(url_for('index'))  # Replace 'index' with your actual endpoint

    # Handle GET request or other cases if necessary
    return render_template('submit_loan.html')

@app.route('/approved')
def approved():
    conn = get_db_connection()
    # Use dictionary=True to get dict results
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch approved users
        cursor.execute('SELECT * FROM users WHERE status = %s', ('approved',))
        approved_users = cursor.fetchall()
        logging.debug(f"Approved users: {approved_users}")

        # Fetch user count
        user_count = get_user_count()

        # Fetch newsletter subscriptions
        subscriptions = get_all_subscriptions()

        # Fetch total amount of deposits
        total_amount = 0
        cursor.execute('SELECT SUM(amount) AS total_amount FROM user_deposits')
        total_amount_result = cursor.fetchone()
        total_amount = total_amount_result['total_amount'] if total_amount_result and total_amount_result['total_amount'] else 0

        # Fetch total number of approved users
        total_approved_users = 0
        cursor.execute(
            'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
        total_approved_users_result = cursor.fetchone()
        total_approved_users = total_approved_users_result[
            'total_approved_users'] if total_approved_users_result else 0

        return render_template('approved.html',
                               approved_users=approved_users,
                               user_count=user_count,
                               subscriptions=subscriptions,
                               total_amount=total_amount,
                               total_approved_users=total_approved_users)

    except Exception as e:
        logging.error(f"Error fetching approved users: {e}")
        return "Error fetching approved users", 500
    finally:
        cursor.close()
        conn.close()


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="loan_auth"
    )


@app.route('/notifications')
def notifications():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier data manipulation

        # Fetch allocation messages from allocation_messages table
        cursor.execute('SELECT session_id, message FROM allocation_messages')
        allocation_messages = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        conn.close()

        # Render template with allocation_messages data
        return render_template('notifications.html', allocation_messages=allocation_messages)

    except mysql.connector.Error as e:
        return f"Error accessing database: {e}"


@app.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT email, username FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute(
            'UPDATE users SET status = %s WHERE id = %s', ('approved', user_id))
        db.commit()

        # Send approval email
        msg = Message('Account Approved',
                      sender='telvinngichukii@gmail.com',
                      recipients=[user['email']])
        msg.body = f"Hello {
            user['username']},\n\nYour account has been approved.\n\nRegards,\nAdmin"
        mail.send(msg)
        flash('User approved successfully.', 'success')

    cursor.close()
    return redirect(url_for('accounts'))

from decimal import Decimal
@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    # Connect to MySQL
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary cursor to fetch data as dictionaries

    # Fetch data from loan_applications table
    query = "SELECT id, username, email, session_id, loan_type, amount, interest, application_date FROM loan_applications"
    cursor.execute(query)
    loan_applications = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()

    return render_template('allocate.html', loan_applications=loan_applications, Decimal=Decimal)

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='loan_auth',
)

@app.route('/update_allocated', methods=['POST'])
def update_allocated():
    if request.method == 'POST':
        username = request.form['username']
        session_id = request.form['session_id']
        email = request.form['email']
        refund = Decimal(request.form['refund'])
        amount = Decimal(request.form['amount']) 

        try:
            with db_connection.cursor() as cursor:
                # Calculate the difference between refund and amount
                difference = refund - amount

                # Save the difference in the total_interests table
                sql_insert = "INSERT INTO total_interests (totals) VALUES (%s)"
                cursor.execute(sql_insert, (difference,))
                db_connection.commit()

                # Update allocated_amount in the loan_applications table
                sql = "UPDATE loan_applications SET allocated_amount = allocated_amount + %s WHERE username = %s AND session_id = %s AND email = %s"
                cursor.execute(sql, (refund, username, session_id, email))
                db_connection.commit()

                # Send email notification
                send_email(username, email, refund)

                # Optionally, you can add more logic here (e.g., logging)
                return redirect(url_for('admin_dashboard'))  # Redirect to your admin dashboard or another route

        except Exception as e:
            # Handle exceptions (e.g., logging, error messages)
            print(f"Error updating allocated_amount: {str(e)}")
            return render_template('error.html', error=str(e))  # Render an error page if needed

        finally:
            db_connection.close()  # Close database connection

    return render_template('allocate.html')

# Function to send email notification
def send_email(username, email, refund):
    try:
        msg = Message(subject="Allocation Update Notification",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[email],
                      body=f"Dear {username},\n\nYour allocated amount has been updated successfully.\n Refund: {refund}\n\nRegards,\nAdmin Team")
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.route('/disapprove_user/<int:user_id>', methods=['POST'])
def disapprove_user(user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT email, username FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if user:
        cursor.execute('UPDATE users SET status = %s WHERE id = %s',
                       ('disapproved', user_id))
        db.commit()

        # Send disapproval email
        msg = Message('Account Disapproved',
                      sender='telvinngichukii@gmail.com',
                      recipients=[user['email']])
        msg.body = f"Hello {
            user['username']},\n\nYour account has been disapproved.\n\nRegards,\nAdmin"
        mail.send(msg)
        flash('User disapproved successfully.', 'error')

    cursor.close()
    return redirect(url_for('accounts'))


def save_message(first_name, last_name, email_address, phone_number, city, message):
    try:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO messages (first_name, last_name, email_address, phone_number, city, message) VALUES (%s, %s, %s, %s, %s, %s)',
            (first_name, last_name, email_address, phone_number, city, message)
        )
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        raise

# Route to submit message


@app.route('/submit_message', methods=['POST'])
def submit_message():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_address = request.form['email_address']
        phone_number = request.form['phone_number']
        city = request.form['city']
        message = request.form['message']

        try:
            save_message(first_name, last_name, email_address,
                         phone_number, city, message)
            return redirect(url_for('index'))
        except Exception as e:
            return f'An error occurred: {e}'

# Function to fetch messages from database


def fetch_messages():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()
        cursor.close()
        return messages
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

# Route to display messages


@app.route('/messages')
def display_messages():
    messages = fetch_messages()
    return render_template('messages.html', messages=messages)

# Function to save deposit to database


def save_deposit(name, email, amount):
    try:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO user_deposits (name, email, amount) VALUES (%s, %s, %s)',
            (name, email, amount)
        )
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        raise


@app.route('/process_deposit', methods=['POST'])
def process_deposit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        phone = request.form['phone']

        try:
            # Save deposit details to database
            save_deposit(name, email, amount)

            # Initiate STK Push payment
            amount_in_cents = amount  # Convert amount to cents
            payment_response = initiate_stk_push(phone, amount_in_cents)

            # Handle payment_response as needed (e.g., logging, error handling)
            print("Payment Response:", payment_response)

            return jsonify({'message': 'Deposit initiated successfully.'})

        except Exception as e:
            return jsonify({'error': f'An error occurred: {e}'}), 500
    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/deposit_section', methods=['GET', 'POST'])
def deposit_section():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']

        try:
            save_deposit(name, email, amount)
            return redirect(url_for('deposit_section'))
        except Exception as e:
            return f'An error occurred: {e}'

    user_count = get_user_count()
    newsletter_count = get_newsletter_subscriptions()
    subscriptions = get_all_subscriptions()
    user = None  # Initialize user object to None
    total_approved_users = 0

    if 'username' in session:
        username = session['username']
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT username, email, phone, profile_photo FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

    # Fetch user deposits from the database
    deposits = []
    total_amount = 0  # Initialize total amount
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT name, email, amount, created_at FROM user_deposits')
    deposits = cursor.fetchall()

    # Calculate total amount
    for deposit in deposits:
        total_amount += deposit['amount']

    # Fetch total number of approved users
    cursor.execute(
        'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
    total_approved_users_result = cursor.fetchone()
    total_approved_users = total_approved_users_result[
        'total_approved_users'] if total_approved_users_result else 0
    cursor.close()

    return render_template('deposit.html',
                           user=user,
                           user_count=user_count,
                           newsletter_count=newsletter_count,
                           subscriptions=subscriptions,
                           deposits=deposits,
                           total_amount=total_amount,
                           total_approved_users=total_approved_users)


# Route for user profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_count = get_user_count()
    newsletter_count = get_newsletter_subscriptions()
    subscriptions = get_all_subscriptions()
    user = None  # Initialize user object to None
    form_data = {}
    form_submitted = False  # Flag to track if the form has been submitted

    # Fetch user deposits from the database
    deposits = []
    total_amount = 0  # Initialize total amount
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT name, email, amount, created_at FROM user_deposits')
    deposits = cursor.fetchall()

    # Calculate total amount
    for deposit in deposits:
        total_amount += deposit['amount']

    # Fetch total number of approved users
    cursor.execute(
        'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
    total_approved_users_result = cursor.fetchone()
    total_approved_users = total_approved_users_result[
        'total_approved_users'] if total_approved_users_result else 0
    cursor.close()

    if 'username' in session:
        username = session['username']
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT username, email, phone, profile_photo FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if request.method == 'POST':
            form_submitted = True  # Set form_submitted to True
            try:
                # Get form data
                form_data = {
                    'first_name': request.form['first_name'],
                    'middle_name': request.form['middle_name'],
                    'last_name': request.form['last_name'],
                    'identification': request.form['identification'],
                    'kra_pin': request.form['kra_pin'],
                    'religion': request.form['religion'],
                    'dob': request.form['dob'],
                    'telephone': request.form['telephone'],
                    'gender': request.form['gender'],
                    'marital_status': request.form['marital_status'],
                    'disability': request.form['disability'],
                    'employed': request.form['employed'],
                    'education': request.form['education'],
                    'po_box': request.form['po_box'],
                    'postal_code': request.form['postal_code'],
                    'town': request.form['town'],
                    'county': request.form['county'],
                    'constituency': request.form['constituency'],
                    'ward': request.form['ward'],
                    # Include session_id in the form data
                    'session_id': session.get('session_id')
                }
                print("Received form data:", form_data)

                # Save form data to database
                cursor = db.cursor()
                sql_query = '''
                    INSERT INTO profile (first_name, middle_name, last_name, identification, kra_pin, religion, dob, telephone, gender, marital_status, disability, employed, education, po_box, postal_code, town, county, constituency, ward, session_id) 
                    VALUES (%(first_name)s, %(middle_name)s, %(last_name)s, %(identification)s, %(kra_pin)s, %(religion)s, %(dob)s, %(telephone)s, %(gender)s, %(marital_status)s, %(disability)s, %(employed)s, %(education)s, %(po_box)s, %(postal_code)s, %(town)s, %(county)s, %(constituency)s, %(ward)s, %(session_id)s)
                '''
                print("Executing SQL query:", sql_query)
                print("With parameters:", form_data)

                cursor.execute(sql_query, form_data)
                db.commit()
                cursor.close()
                print("Data saved successfully")
                return redirect(url_for('profile'))
            except Exception as e:
                print("Error occurred:", str(e))
                return 'An error occurred: ' + str(e)

    return render_template('profile.html',
                           user=user,
                           user_count=user_count,
                           newsletter_count=newsletter_count,
                           subscriptions=subscriptions,
                           deposits=deposits,
                           total_amount=total_amount,
                           form_data=form_data,
                           form_submitted=form_submitted,
                           total_approved_users=total_approved_users)


# Function to get user count from database


def get_user_count():
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) AS user_count FROM users')
    result = cursor.fetchone()
    cursor.close()
    return result[0]

# Function to get newsletter subscriptions count from database


def get_newsletter_subscriptions():
    cursor = db.cursor()
    cursor.execute(
        'SELECT COUNT(*) AS newsletter_count FROM newsletter_subscriptions')
    result = cursor.fetchone()
    cursor.close()
    return result[0]

# Function to get all newsletter subscriptions from database


def get_all_subscriptions():
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'SELECT email, DATE(subscription_date) AS subscription_date FROM newsletter_subscriptions')
    subscriptions = cursor.fetchall()
    cursor.close()
    return subscriptions

# Function to save newsletter subscription to database


def save_subscription(session_id, email):
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO newsletter_subscriptions (session_id, email) VALUES (%s, %s)', (session_id, email))
    db.commit()
    cursor.close()




# Route for logging out users
@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        cursor = db.cursor()
        cursor.execute(
            'UPDATE users SET session_id = NULL WHERE username = %s', (username,))
        db.commit()
        cursor.close()

    session.pop('username', None)
    session.pop('session_id', None)
    return redirect(url_for('index'))

# Route for subscribing users to newsletter


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        # Generate session_id if not logged in
        session_id = session.get('session_id', str(uuid.uuid4()))
        save_subscription(session_id, email)
        return redirect(url_for('index'))
    else:
        return 'Email is required', 400

# Function to get all users from database


def get_users():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        cursor.close()
        print(users)  # Print fetched users
        return users
    except Exception as e:
        print(f"Error occurred while fetching users: {e}")  # Print any errors
        return []

# Route for displaying users (for admin dashboard, etc.)


@app.route('/users')
def display_users():
    users = get_users()
    return render_template('client_dash.html', users=users)


# Function to generate password for STK Push
business_short_code = '174379'
passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
consumer_key = 'rewKsu3rtjDzN2CcevxZMlpWXdkFifLvUBF3rYOGFJdCifFV'
consumer_secret = '0wd8tAEOGUZQaHBFGs0juiiHiNpGUr3dPOgU8NpY0h5HYTpaGHmfdMT30Ae1gvAm'
callback_nurl = 'https://3486-102-0-5-78.ngrok-free.app/callback_url'

def generate_password():
    return base64.b64encode((business_short_code + passkey + timestamp).encode()).decode('utf-8')

def initiate_stk_push(phone_number, amount):
    password = generate_password()

    # Access Token Request
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((consumer_key + ':' + consumer_secret).encode()).decode('utf-8')
    }
    response = requests.get(access_token_url, headers=headers)
    access_token = response.json()['access_token']

    # STK Push Request
    stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': business_short_code,
        'PhoneNumber': phone_number,
        'CallBackURL': callback_nurl,
        'AccountReference': '2255',  # Example account reference
        'TransactionDesc': 'Test Payment'
    }

    # Print payload for debugging
    print("Payload:", payload)

    response = requests.post(stk_push_url, json=payload, headers=headers)

    return response.json()


# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return 'Passwords do not match'

        if 'profile_photo' not in request.files:
            return 'No file part'
        file = request.files['profile_photo']

        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_photo_path = os.path.join('static', 'uploads', filename)
        else:
            return 'File not allowed'

        hashed_password = generate_password_hash(password)

        # Save user details to database (you might need to adjust this based on your DB schema)
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, email, phone, profile_photo, password) VALUES (%s, %s, %s, %s, %s)',
                       (username, email, phone, profile_photo_path, hashed_password))
        db.commit()
        cursor.close()

        # Store username and email in session
        session['username'] = username
        session['email'] = email

        # Initiate STK Push payment
        amount = '1'  # Example amount
        payment_response = initiate_stk_push(phone, amount)

        # Handle payment_response as needed (e.g., logging, error handling)
        print("Payment Response:", payment_response)

        # Redirect to login page after successful signup
        return redirect(url_for('login'))

    return render_template('signup.html')

# Endpoint to handle M-Pesa callback
@app.route('/callback_url', methods=['POST'])
def callback_url():
    try:
        # Get JSON data from the request
        mpesa_response = request.get_json()

        if mpesa_response is None:
            return jsonify({"error": "No JSON data received"}), 400

        # Log the response to a file
        log_file = "M_PESAConfirmationResponse.txt"
        with open(log_file, "a") as log:
            log.write(f"{datetime.now()} - Received M-Pesa Callback:\n")
            log.write(f"{mpesa_response}\n\n")

        # Example: Extract relevant data from mpesa_response
        result_code = mpesa_response.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        result_desc = mpesa_response.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
        merchant_request_id = mpesa_response.get('Body', {}).get('stkCallback', {}).get('MerchantRequestID')
        checkout_request_id = mpesa_response.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

        # Your processing logic here...

        response = {
            "ResultCode": 0,
            "ResultDesc": "Confirmation Received Successfully"
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to view deposits


@app.route('/view_deposits')
def view_deposits():
    try:
        # Use the existing db connection
        cursor = db.cursor(dictionary=True)

        # Execute SQL query to fetch all deposits
        cursor.execute("SELECT * FROM user_deposits")
        deposits = cursor.fetchall()
        logging.debug(f"Deposits: {deposits}")

        # Fetch total number of users
        cursor.execute('SELECT COUNT(*) AS total_users FROM users')
        total_users_result = cursor.fetchone()
        total_users = total_users_result['total_users'] if total_users_result else 0
        logging.debug(f"Total users: {total_users}")

        # Fetch total deposits
        cursor.execute(
            'SELECT SUM(amount) AS total_deposits FROM user_deposits')
        total_deposits_result = cursor.fetchone()
        total_deposits = total_deposits_result['total_deposits'] if total_deposits_result else 0
        logging.debug(f"Total deposits: {total_deposits}")

        # Fetch total number of approved users
        cursor.execute(
            'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
        total_approved_users_result = cursor.fetchone()
        total_approved_users = total_approved_users_result[
            'total_approved_users'] if total_approved_users_result else 0
        logging.debug(f"Total approved users: {total_approved_users}")

        # Close cursor
        cursor.close()

        return render_template('view_deposits.html',
                               deposits=deposits,
                               total_users=total_users,
                               total_deposits=total_deposits,
                               total_approved_users=total_approved_users)

    except mysql.connector.Error as error:
        logging.error(f"Error connecting to MySQL: {error}")
        # Handle the error appropriately, e.g., render an error page
        return f"Error connecting to MySQL: {error}", 500

from decimal import Decimal
@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = db.cursor(dictionary=True)

    try:
        # Fetch approved users
        cursor.execute('SELECT * FROM users WHERE status = %s', ('approved',))
        approved_users = cursor.fetchall()
        logging.debug(f"Approved users: {approved_users}")

        # Fetch pending users
        cursor.execute('SELECT * FROM users WHERE status = %s', ('pending',))
        pending_users = cursor.fetchall()
        logging.debug(f"Pending users: {pending_users}")

        # Execute SQL query to calculate sum of totals
        cursor.execute('SELECT SUM(totals) AS total_interests FROM total_interests')
        total_interests_result = cursor.fetchone()
        total_sum = total_interests_result['total_interests'] if total_interests_result['total_interests'] is not None else 0
        logging.debug(f"Total sum of interests: {total_sum}")

        # Fetch not approved users
        cursor.execute('SELECT * FROM users WHERE status = %s',
                       ('not approved',))
        not_approved_users = cursor.fetchall()
        logging.debug(f"Not approved users: {not_approved_users}")

        # Fetch total number of users
        cursor.execute('SELECT COUNT(*) AS total_users FROM users')
        total_users_result = cursor.fetchone()
        total_users = total_users_result['total_users'] if total_users_result else 0
        logging.debug(f"Total users: {total_users}")

        # Fetch total deposits
        cursor.execute(
            'SELECT SUM(amount) AS total_deposits FROM user_deposits')
        total_deposits_result = cursor.fetchone()
        total_deposits = total_deposits_result['total_deposits'] if total_deposits_result else 0
        logging.debug(f"Total deposits: {total_deposits}")

        # Fetch total number of approved users
        cursor.execute(
            'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
        total_approved_users_result = cursor.fetchone()
        total_approved_users = total_approved_users_result[
            'total_approved_users'] if total_approved_users_result else 0
        logging.debug(f"Total approved users: {total_approved_users}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        cursor.close()

    return render_template('admin.html',
                           approved_users=approved_users,
                           pending_users=pending_users,
                           not_approved_users=not_approved_users,
                           total_sum=str(total_sum),
                           total_users=total_users,
                           total_deposits=total_deposits,
                           total_approved_users=total_approved_users)


@app.route('/accounts')
def accounts():
    cursor = db.cursor(dictionary=True)

    try:
        # Fetch all users
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        logging.debug(f"Users: {users}")

        # Fetch total number of users
        cursor.execute('SELECT COUNT(*) AS total_users FROM users')
        total_users_result = cursor.fetchone()
        total_users = total_users_result['total_users'] if total_users_result else 0
        logging.debug(f"Total users: {total_users}")

        # Fetch total deposits
        cursor.execute(
            'SELECT SUM(amount) AS total_deposits FROM user_deposits')
        total_deposits_result = cursor.fetchone()
        total_deposits = total_deposits_result['total_deposits'] if total_deposits_result else 0
        logging.debug(f"Total deposits: {total_deposits}")

        # Fetch total number of approved users
        cursor.execute(
            'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
        total_approved_users_result = cursor.fetchone()
        total_approved_users = total_approved_users_result[
            'total_approved_users'] if total_approved_users_result else 0
        logging.debug(f"Total approved users: {total_approved_users}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        cursor.close()

    return render_template('accounts.html',
                           users=users,
                           total_users=total_users,
                           total_deposits=total_deposits,
                           total_approved_users=total_approved_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check for admin credentials
        if username == 'admin' and password == 'admin123':
            session['username'] = 'admin'
            # Change this to your eadmin dashboard route
            return redirect(url_for('admin_dashboard'))

        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session_id = str(uuid.uuid4())
            cursor = db.cursor()
            cursor.execute(
                'UPDATE users SET session_id = %s WHERE id = %s', (session_id, user['id']))
            db.commit()
            cursor.close()

            session['username'] = user['username']
            session['session_id'] = session_id
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

# Main route (homepage)


@app.route('/')
def index():
    user_count = get_user_count()
    newsletter_count = get_newsletter_subscriptions()
    messages = fetch_messages()
    subscriptions = get_all_subscriptions()
    users = get_users()
    total_approved_users = 0

    if 'username' in session:
        username = session['username']
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT username, email, phone, profile_photo FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user:
            # Fetch user deposits from the database
            deposits = []
            total_amount = 0  # Initialize total amount
            cursor.execute(
                'SELECT name, email, amount, created_at FROM user_deposits')
            deposits = cursor.fetchall()

            # Calculate total amount
            for deposit in deposits:
                total_amount += deposit['amount']

            # Fetch total number of approved users
            cursor.execute(
                'SELECT COUNT(*) AS total_approved_users FROM users WHERE status = %s', ('approved',))
            total_approved_users_result = cursor.fetchone()
            total_approved_users = total_approved_users_result[
                'total_approved_users'] if total_approved_users_result else 0

            # Execute SQL query to calculate sum of totals
            cursor.execute('SELECT SUM(totals) AS total_interests FROM total_interests')
            total_interests_result = cursor.fetchone()
            total_sum = total_interests_result['total_interests'] if total_interests_result['total_interests'] is not None else 0
            logging.debug(f"Total sum of interests: {total_sum}")

            cursor.close()

            return render_template('client_dash.html',
                                   user=user,
                                   users=users,
                                   user_count=user_count,
                                   deposits=deposits,
                                   newsletter_count=newsletter_count,
                                   total_sum=total_sum,
                                   messages=messages,
                                   subscriptions=subscriptions,
                                   total_amount=total_amount,
                                   total_approved_users=total_approved_users)

    return render_template('home.html',
                           user_count=user_count,
                           newsletter_count=newsletter_count,
                           messages=messages,
                           subscriptions=subscriptions)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
