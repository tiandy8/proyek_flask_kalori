# Corrected app.py - PLEASE USE THIS EXACT CODE

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from chatbot import get_gemini_response, analyze_food_image

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

# Meal Model
class Meal(db.Model):
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    calories = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('meals', lazy=True))

# Food Image Model
class FoodImage(db.Model):
    __tablename__ = 'food_image'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_result = db.Column(db.Text)
    calories = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('food_images', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's meals for today
    today = datetime.utcnow().date()
    meals = Meal.query.filter_by(user_id=current_user.id, date=today).all()
    
    # Get user's food images
    food_images = FoodImage.query.filter_by(user_id=current_user.id).order_by(FoodImage.upload_time.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         title='Dashboard',
                         meals=meals,
                         food_images=food_images)

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
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login Failed. Check username and password.', 'danger')

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
@login_required
def chatbot_ask():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    bot_response = get_gemini_response(user_message)
    return jsonify({'reply': bot_response})

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
        
        # Analyze the image
        analysis_result = analyze_food_image(image_data)
        
        # Save the image analysis to database
        new_image = FoodImage(
            user_id=current_user.id,
            filename=image_file.filename,
            analysis_result=analysis_result
        )
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({'analysis': analysis_result})
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": "Error processing image"}), 500

@app.route('/test_gemini')
@login_required
def test_gemini():
    try:
        # Simple test message
        test_message = "What is the calorie content of an apple?"
        response = get_gemini_response(test_message)
        
        if response and len(response) > 0:
            return jsonify({
                'status': 'success',
                'message': 'Gemini API is working correctly!',
                'test_response': response
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Gemini API returned empty response'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error testing Gemini API: {str(e)}'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create any missing tables
    app.run(debug=True)