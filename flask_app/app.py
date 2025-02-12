
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from auth import authenticate_user, register_user
from flask_migrate import Migrate
from models import db, User, init_db
from config import Config
from flask import jsonify
from data_loader.data_loader import load_parquet
from data_loader.data_processor import process_stock_data

# ================== 配置区域 ==================
# Define the base path of the app
base_path = os.path.abspath(os.path.dirname(__file__))

# Folder paths
TEMPLATES_FOLDER = os.path.join(base_path, 'templates')
STATIC_FOLDER = os.path.join(base_path, 'static')
print('TEMPLATES_FOLDER:', TEMPLATES_FOLDER)
print('STATIC_FOLDER:', STATIC_FOLDER)

# ================== 初始化区域 ==================
# Initialize Flask app with template and static folder paths
app = Flask(__name__, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)
app.config.from_object(Config)


# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Load Parquet file at app startup
parquet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'merged_data.parquet'))
df = load_parquet(parquet_file_path)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    init_db(app)

# Root route
@app.route('/')
def home():
    return render_template('index.html')  

# Register page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        # Check if passwords match
        if password != password2:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Register the user
        if register_user(username, email, password):
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User already exists.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form  # True if checkbox is checked
        user = authenticate_user(username, password)
        if user:
            login_user(user, remember=remember)  # Pass 'remember' to login_user
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')  # Flash error message
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Protected page (only accessible by logged-in users)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# Add a new route for the stock page
@app.route('/stock')
@login_required
def stock():
    return render_template('stock.html', username=current_user.username)

@app.route('/stock_data')
@login_required
def stock_data():
    ts_code = request.args.get('ts_code')
    if not ts_code:
        return jsonify({'error': 'Missing ts_code parameter'}), 400

    stock_data = df[df['ts_code'] == ts_code]
    if stock_data.empty:
        return jsonify({'error': 'No data found for this ts_code'}), 404

    chart_data = process_stock_data(stock_data)
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True)
