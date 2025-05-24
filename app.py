# Corrected app.py - PLEASE USE THIS EXACT CODE

from flask import Flask, render_template, request # Removed semicolon
from config import Config
# Removed duplicate import of SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, flash
from flask import jsonify # Import jsonify
from chatbot import get_gemini_response # Import your chatbot function


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # __repr__ INSIDE the class
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# REMOVED duplicate __repr__ from outside the class

# CORRECTED decorator: user_loader (with 'r')
@login_manager.user_loader
def load_user(user_id):
    # --- DEBUG START ---
    print(f"--- Attempting to load user_id: {user_id} ---")
    user = User.query.get(int(user_id))
    print(f"User found by load_user: {user}")
    # --- DEBUG END ---
    return user # Return the found user object


@app.route('/')
def index():
    # Assuming index.html exists
    return render_template('index.html', title='Home')

# Assuming dashboard.html exists
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

# Route for Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Added .strip()
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        # --- DEBUG START ---
        print(f"\n--- Registration Attempt ---")
        print(f"Username entered: '{username}'")
        print(f"Email entered: '{email}'")
        # --- DEBUG END ---

        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()

        if user_by_username:
            flash('Username already taken.', 'warning')
        elif user_by_email:
            flash('Email already registered.', 'warning')
        elif not password: # Added check for empty password
             flash('Password cannot be empty.', 'warning')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)

           # --- Existing code before commit ---
            print(f"Generated password hash (before commit): {new_user.password_hash}")
            # --- END DEBUG ---

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                print(f"User '{username}' commit reported successful.") # DEBUG

                # ===> ADD THIS BLOCK TO CHECK AFTER COMMIT <===
                try:
                    user_from_db_after_commit = User.query.filter_by(username=username).first()
                    if user_from_db_after_commit:
                        print(f"Hash read back from DB (after commit): {user_from_db_after_commit.password_hash}")
                        # Compare the hash generated before commit with the one read back
                        if new_user.password_hash == user_from_db_after_commit.password_hash:
                            print("SUCCESS: Hash in DB matches hash generated before commit.")
                        else:
                            print("ERROR: Hash in DB DOES NOT MATCH hash generated before commit!")
                    else:
                        print("ERROR: Could not re-query user immediately after commit.")
                except Exception as query_e:
                    print(f"ERROR querying user after commit: {query_e}")
                # ===> END OF ADDED BLOCK <===

                return redirect(url_for('login'))
            except Exception as e:
                 db.session.rollback()
                 flash('An error occurred during registration. Please try again.', 'danger')
                 print(f"Database commit error during registration: {e}") # DEBUG

    # Assuming register.html exists
    return render_template('register.html', title='Register')

# Route for Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Added .strip()
        username = request.form['username'].strip()
        password = request.form['password']

        # --- DEBUG START ---
        print(f"\n--- Login Attempt ---")
        print(f"Username from form: '{username}'")
        # --- DEBUG END ---

        user = User.query.filter_by(username=username).first()
        password_match = False # Initialize

        # --- DEBUG START ---
        if user:
            print(f"User found in DB: {user}")
            print(f"Stored hash in DB: {user.password_hash}")
            password_match = user.check_password(password)
            print(f"Result of check_password for entered password: {password_match}")
        else:
            print(f"User '{username}' not found in DB.")
        # --- DEBUG END ---

        if user and password_match: # Check result variable
            login_user(user, remember=request.form.get('remember'))
            print(f"Login successful for user: {username}") # DEBUG
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login Failed. Check username and password.', 'danger')
            print(f"Login failed for username: {username}") # DEBUG

    # Assuming login.html exists
    return render_template('login.html', title='Login')

# Route for Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/chatbot_ask', methods=['POST'])
@login_required # Only logged-in users can use the chatbot
def chatbot_ask():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    # --- DEBUG ---
    print(f"Received message for chatbot: {user_message}")
    # --- END DEBUG ---

    bot_response = get_gemini_response(user_message)

    # --- DEBUG ---
    print(f"Sending response from chatbot: {bot_response}")
     # --- END DEBUG ---

    return jsonify({'reply': bot_response})

if __name__ == '__main__':
    app.run(debug=True)