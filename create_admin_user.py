# create_admin_user.py
import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User, ROLES # Importez ROLES aussi
from getpass import getpass # Pour demander le mot de passe de manière sécurisée

def create_admin():
    app = create_app()
    with app.app_context():
        print("\n--- Creating Admin User ---")
        
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        password = getpass("Enter admin password: ") # Cache le mot de passe tapé
        confirm_password = getpass("Confirm admin password: ")

        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        existing_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if existing_user:
            print(f"User '{username}' already exists. Skipping creation.")
            return

        new_admin = User(username=username, email=email, role='ADMIN') 
        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully with role 'ADMIN'!") # Message mis à jour
        print("--- Admin User Creation Finished ---")

if __name__ == '__main__':
    create_admin()