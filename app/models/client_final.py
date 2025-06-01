# app/models/client_final.py
from app import db

class ClientFinal(db.Model):
    __tablename__ = 'client_final'

    id_client_final = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    adresse = db.Column(db.String(255))
    numero_telephone = db.Column(db.String(20))
    email = db.Column(db.String(120)) # L'email d'un client final n'est pas forcément unique car il peut s'agir de points de livraison différents pour le même client initial, avec le même contact.

    # Clé étrangère vers ClientInitial (un client final est souvent rattaché à un client initial / entreprise)
    # Selon le diagramme : #IdClientInitial. On le rend nullable=False si un client final DOIT appartenir à un client initial.
    id_client_initial = db.Column(db.Integer, db.ForeignKey('client_initial.id_client_initial'), nullable=False)

    # Relation avec ClientInitial
    client_initial = db.relationship('ClientInitial', backref='clients_final', lazy=True)
    
    # Relations vers DetailCommande (définie sur l'autre côté pour éviter les dépendances circulaires)
    # details_commandes = db.relationship('DetailCommande', backref='client_final', lazy=True)

    def __repr__(self):
        return f"<ClientFinal {self.nom} {self.prenom or ''}>"

    def to_dict(self):
        return {
            'id_client_final': self.id_client_final,
            'nom': self.nom,
            'prenom': self.prenom,
            'adresse': self.adresse,
            'numero_telephone': self.numero_telephone,
            'email': self.email,
            'id_client_initial': self.id_client_initial,
            'client_initial_nom': self.client_initial.nom if self.client_initial else None
        }