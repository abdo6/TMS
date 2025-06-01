# app/config/settings.py

# Clé secrète pour les sessions Flask (changez-la pour une vraie clé forte en production !)
SECRET_KEY = 'super_secret_key_a_changer_absolument'

# Configuration de la base de données PostgreSQL
# format: 'postgresql://utilisateur:mot_de_passe@host:port/nom_base_de_donnees'
SQLALCHEMY_DATABASE_URI = 'postgresql://tms_user:tms_pass123@localhost:5432/tms_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False # Désactive le suivi des modifications des objets SQLAlchemy, économise des ressources

# Assurez-vous de remplacer 'votre_mot_de_passe_secure' par le mot de passe que vous avez défini pour 'tms_user'