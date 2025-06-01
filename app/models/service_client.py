# app/models/service_client.py
from app import db

class ServiceClient(db.Model):
    __tablename__ = 'service_client'

    id_service = db.Column(db.Integer, primary_key=True)
    nom_service = db.Column(db.String(100), nullable=False)

    # Clé étrangère vers ClientInitial (un ServiceClient appartient à un ClientInitial)
    id_client_initial = db.Column(db.Integer, db.ForeignKey('client_initial.id_client_initial'), nullable=False)
    
    # Relation pour accéder au client initial associé
    client_initial = db.relationship('ClientInitial', backref='services_clients', lazy=True)

    def __repr__(self):
        return f"<ServiceClient {self.nom_service} (Client: {self.client_initial.nom})>"

    def to_dict(self):
        return {
            'id_service': self.id_service,
            'nom_service': self.nom_service,
            'id_client_initial': self.id_client_initial,
            'client_initial_nom': self.client_initial.nom if self.client_initial else None
        }