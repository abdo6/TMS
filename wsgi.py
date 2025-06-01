# wsgi.py

import sys
import os

# Add the project root directory to the Python path
# Your PythonAnywhere username is 'ghabaoui' and your repository folder is 'TMS'
# So, the full path to your project will be /home/ghabaoui/TMS
project_root = '/home/ghabaoui/TMS'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the create_app function from your 'app' package
# Your Flask application instance is created by calling create_app()
from app import create_app

# Create the Flask application instance
# PythonAnywhere expects this object to be named 'application'
application = create_app()