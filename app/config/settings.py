# app/config/settings.py

import os # <--- AJOUTEZ CET IMPORT

# Clé secrète pour les sessions Flask
# Utilise la variable d'environnement SECRET_KEY si elle existe, sinon utilise la valeur par défaut pour le développement local
SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secret_key_a_changer_absolument')

# Configuration de la base de données PostgreSQL
# Utilise la variable d'environnement DATABASE_URL fournie par Render, sinon utilise la valeur locale
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://tms_user:tms_pass123@localhost:5432/tms_db')
SQLALCHEMY_TRACK_MODIFICATIONS = False