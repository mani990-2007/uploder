from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to generate random string for shareable link
def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# Function to get port from user input
def get_port_from_user():
    while True:
        try:
            port = int(input("Enter the port number to run the web app on localhost (default is 5000): "))
            return port
        except ValueError:
            print("Invalid port number! Please enter a valid integer.")

# Get port number from user
port = get_port_from_user()

# Function to save user credentials to a text file
def save_user(username, password):
    with open('users.txt', 'a', encoding='utf-8') as file:
        file.write(f'{username}:{password}\n')

# Function to check user credentials from the text file
def check_credentials(username, password):
    with open('users.txt', 'r', encoding='utf-8') as file:
        for line in file:
            stored_username, stored_password = line.strip().split(':')
            if username == stored_username and password == stored_password:
                return True
    return False

# Function to create user directory if it doesn't exist
def create_user_directory(username):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

# Function to update user credentials in the text file
def update_user_credentials(current_username, new_username, new_password):
    with open('users.txt', 'r', encoding='utf-8') as file:
        users = file.readlines()

    with open('users.txt', 'w', encoding='utf-8') as file:
        for user in users:
            username, password = user.strip().split(':')
            if username == current_username:
                if new_username:
                    username = new_username
                if new_password:
                    password = new_password
                file.write(f'{username}:{password}\n')
            else:
                file.write(user)

# Route for sharing file
@app.route('/share/<username>/<filename>')
def share(username, filename):
    download_link = request.host_url.rstrip('/') + f"/download/{username}/{filename}"
    return render_template('share.html', download_link=download_link)

# Route for displaying download page
@app.route('/download/<username>/<filename>')
def download_page(username, filename):
    return render_template('download.html', username=username, filename=filename)

# Route for downloading shared files
@app.route('/shared/<username>/<filename>')
def download_shared_file(username, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    return send_from_directory(user_folder, filename, as_attachment=True)

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username  # Store username in session
            create_user_directory(username)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        with open('users.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if username == line.split(':')[0]:
                    flash('Username already exists!', 'error')
                    return redirect(url_for('register'))

        # Save user credentials to the text file
        save_user(username, password)
        create_user_directory(username)
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        current_username = session.get('username')

        if not check_credentials(current_username, old_password):
            flash('Incorrect current password.', 'error')
            return redirect(url_for('account'))

        update_user_credentials(current_username, new_username, new_password)
        session['username'] = new_username if new_username else current_username
        flash('Account updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('account.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
            file_path = os.path.join(user_folder, filename)
            file.save(file_path)
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('upload_file'))

    return render_template('upload.html')

@app.route('/file_table')
def file_table():
    if session.get('logged_in'):
        username = session.get('username')
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        files = []
        if os.path.exists(user_folder):
            files = os.listdir(user_folder)
            # Add upload date to each file (using file modification time)
            files_with_dates = []
            for file in files:
                file_path = os.path.join(user_folder, file)
                modification_time = os.path.getmtime(file_path)
                upload_date = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')
                files_with_dates.append({'name': file, 'upload_date': upload_date})
            return render_template('file_table.html', files=files_with_dates)
        else:
            flash('No files uploaded yet.', 'info')
            return render_template('file_table.html', files=files)
    else:
        return redirect(url_for('login'))

@app.route('/delete_file/<filename>')
def delete_file(filename):
    if session.get('logged_in'):
        username = session.get('username')
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        file_path = os.path.join(user_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'File "{filename}" deleted successfully!', 'success')
        else:
            flash(f'File "{filename}" not found!', 'error')
        return redirect(url_for('file_table'))
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
