# app/models/entete_commande.py
from app import db

class EnteteCommande(db.Model):
    __tablename__ = 'entete_commande'

    id_entete_commande = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False) # Une référence unique pour la commande
    date_commande = db.Column(db.Date, nullable=False, default=db.func.current_date()) # Date de création de la commande

    # Clés étrangères
    id_client_initial = db.Column(db.Integer, db.ForeignKey('client_initial.id_client_initial'), nullable=False)
    id_service = db.Column(db.Integer, db.ForeignKey('service_client.id_service'), nullable=False)

    # Relations
    client_initial = db.relationship('ClientInitial', backref='entetes_commandes', lazy=True)
    service_client = db.relationship('ServiceClient', backref='entetes_commandes', lazy=True)
    
    # Relation vers DetailCommande (les lignes de commande de cette entête)
    # details_commandes = db.relationship('DetailCommande', backref='entete_commande', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"<EnteteCommande {self.reference} (Client: {self.client_initial.nom})>"

    def to_dict(self):
        return {
            'id_entete_commande': self.id_entete_commande,
            'reference': self.reference,
            'date_commande': self.date_commande.isoformat(),
            'id_client_initial': self.id_client_initial,
            'client_initial_nom': self.client_initial.nom if self.client_initial else None,
            'id_service': self.id_service,
            'service_client_nom': self.service_client.nom_service if self.service_client else None
        }