# Corrected app.py - PLEASE USE THIS EXACT CODE

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from chatbot import get_chat_response, analyze_food_image

app = Flask(__name__)
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Food Entry Model (Unified)
class FoodEntry(db.Model):
    __tablename__ = 'food_entry'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    calories = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    
    # Image-related fields (optional)
    image_filename = db.Column(db.String(255), nullable=True)
    image_analysis = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', backref=db.backref('food_entries', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        print(f"Dashboard accessed by user: {current_user.username}")
        print(f"Session data: {dict(session)}")
        
        # Get user's food entries for today
        today = datetime.utcnow().date()
        food_entries = FoodEntry.query.filter(
            FoodEntry.user_id == current_user.id,
            db.func.date(FoodEntry.date) == today
        ).all()
        print(f"Found {len(food_entries)} food entries for today")
        
        return render_template('dashboard.html', 
                             title='Dashboard',
                             food_entries=food_entries)
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()

        if user_by_username:
            flash('Username already taken.', 'warning')
        elif user_by_email:
            flash('Email already registered.', 'warning')
        elif not password:
            flash('Password cannot be empty.', 'warning')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'danger')
                print(f"Database commit error during registration: {e}")

    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("User already authenticated, redirecting to dashboard")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        remember = request.form.get('remember', False)
        
        print(f"Login attempt - Username: {username}, Remember: {remember}")
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found in database: {user.username}")
            if user.check_password(password):
                print("Password verification successful")
                try:
                    login_user(user, remember=remember)
                    session.permanent = True  # Make the session permanent
                    print(f"User logged in successfully: {user.username}")
                    print(f"Session data: {dict(session)}")
                    
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = url_for('dashboard')
                    
                    print(f"Redirecting to: {next_page}")
                    return redirect(next_page)
                except Exception as e:
                    print(f"Error during login: {str(e)}")
                    flash('An error occurred during login. Please try again.', 'danger')
            else:
                print("Password verification failed")
                flash('Invalid password.', 'danger')
        else:
            print(f"User not found: {username}")
            flash('Username not found.', 'danger')
    
    return render_template('login.html', title='Login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', title='Chat with NutriBot')

@app.route('/chatbot_ask', methods=['POST'])
def chatbot_ask():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data['message']
        
        if not message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        print(f"Received message: {message}")
        
        response = get_chat_response(message)
        print(f"Bot response: {response}")
        
        return jsonify({'reply': response})
    except Exception as e:
        print(f"Error in chatbot_ask: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_food_image', methods=['POST'])
@login_required
def analyze_food_image_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Read the image file
        image_data = image_file.read()
        
        # Check if the file is actually an image
        if not image_file.content_type.startswith('image/'):
            return jsonify({"error": "File must be an image"}), 400
        
        # Analyze the image
        analysis_result = analyze_food_image(image_data)
        
        if analysis_result.startswith("Sorry"):
            return jsonify({"error": analysis_result}), 400
        
        # Save the food entry with image analysis
        new_entry = FoodEntry(
            user_id=current_user.id,
            name=image_file.filename,  # Default name from filename
            image_filename=image_file.filename,
            image_analysis=analysis_result,
            date=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({
            'analysis': analysis_result,
            'message': 'Image analyzed successfully'
        })
    except Exception as e:
        print(f"Error processing image: {e}")
        db.session.rollback()
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

@app.route('/test_chat')
def test_chat():
    try:
        # Test nutrition query
        nutrition_response = get_chat_response("What are the health benefits of eating fruits?", "nutrition")
        print("Nutrition response:", nutrition_response)
        
        # Test meal planning query
        meal_planning_response = get_chat_response("Can you suggest a simple meal plan for a week?", "meal_planning")
        print("Meal planning response:", meal_planning_response)
        
        return jsonify({
            'nutrition_test': nutrition_response,
            'meal_planning_test': meal_planning_response
        })
    except Exception as e:
        print(f"Error in test_chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/track-meal')
@login_required
def track_meal():
    # Get user's food entries
    food_entries = FoodEntry.query.filter_by(user_id=current_user.id).order_by(FoodEntry.date.desc()).all()
    return render_template('analyze_food.html', food_entries=food_entries)

@app.route('/analyze-food')
@login_required
def analyze_food():
    # Get user's food entries
    food_entries = FoodEntry.query.filter_by(user_id=current_user.id).order_by(FoodEntry.date.desc()).all()
    return render_template('analyze_food.html', food_entries=food_entries)

@app.route('/log_meal', methods=['POST'])
@login_required
def log_meal():
    try:
        data = request.get_json()
        
        # Create new food entry
        new_entry = FoodEntry(
            user_id=current_user.id,
            name=data.get('name'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            carbs=data.get('carbs'),
            fat=data.get('fat'),
            description=data.get('description'),
            date=datetime.utcnow()
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Meal logged successfully',
            'entry': {
                'id': new_entry.id,
                'name': new_entry.name,
                'calories': new_entry.calories,
                'date': new_entry.date.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        print(f"Error logging meal: {e}")
        db.session.rollback()
        return jsonify({"error": f"Error logging meal: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create any missing tables
    app.run(debug=True)