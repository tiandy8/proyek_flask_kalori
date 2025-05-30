from app import app, db, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create a test user
        test_user = User(
            username='test',
            email='test@example.com'
        )
        test_user.set_password('password123')
        
        # Add the test user to the database
        db.session.add(test_user)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
            print("Test user created:")
            print("Username: test")
            print("Password: password123")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db() 