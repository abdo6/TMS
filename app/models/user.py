# app/models/user.py
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

ROLES = {
    'ADMIN': 'Administrateur',
    'RH': 'Ressources Humaines',
    'PLANIFIER': 'Planificateur',
    'CLIENT': 'Client',
    'COMMERCIAL': 'Commercial',
    'CHARGE_EXPLOITATION': 'Chargé d\'exploitation',
    'APPROVISIONNEUR': 'Approvisionneur',
    'CHARGE_MAINTENANCE': 'Chargé de maintenance',
    'CHAUFFEUR': 'Chauffeur' # <--- AJOUTEZ CE NOUVEAU RÔLE
}

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='CLIENT') 

    # Clé étrangère et relation pour le rôle CLIENT
    id_client_initial = db.Column(db.Integer, db.ForeignKey('client_initial.id_client_initial'), nullable=True)
    client_initial_data = db.relationship('ClientInitial', backref='user_account', uselist=False)

    # NOUVELLE CLÉ ÉTRANGÈRE ET RELATION pour le rôle CHAUFFEUR
    id_chauffeur = db.Column(db.Integer, db.ForeignKey('chauffeur.id_chauffeur'), nullable=True)
    chauffeur_data = db.relationship('Chauffeur', backref='user_account', uselist=False) # uselist=False car un User est lié à un seul Chauffeur

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'id_client_initial': self.id_client_initial,
            'id_chauffeur': self.id_chauffeur # <--- AJOUTEZ POUR L'INFO
        }