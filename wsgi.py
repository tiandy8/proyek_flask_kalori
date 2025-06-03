import sys
import os

# Add your project's directory to the Python path
project_home = os.path.abspath(os.path.dirname(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import your Flask app instance
# Assuming your main Flask app file is app.py and the Flask object is named 'app'
from app import app as application 