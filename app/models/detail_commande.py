# app/models/detail_commande.py
from app import db

class DetailCommande(db.Model):
    __tablename__ = 'detail_commande'

    id_detail_commande = db.Column(db.Integer, primary_key=True)
    quantite = db.Column(db.Integer, nullable=False)
    description_colis = db.Column(db.String(255))
    volume = db.Column(db.Numeric(10, 2))
    poids = db.Column(db.Numeric(10, 2))

    id_entete_commande = db.Column(db.Integer, db.ForeignKey('entete_commande.id_entete_commande'), nullable=False)
    id_type_vehicule = db.Column(db.Integer, db.ForeignKey('type_vehicule.id_type_vehicule'), nullable=False)
    id_client_final = db.Column(db.Integer, db.ForeignKey('client_final.id_client_final'), nullable=False)
    id_destination = db.Column(db.Integer, db.ForeignKey('destination.id_destination'), nullable=False)

    entete_commande = db.relationship('EnteteCommande', backref='details_commandes_rel', lazy=True) # Renommé backref pour éviter le conflit avec 'details_commandes' de Mission
    type_vehicule = db.relationship('TypeVehicule', backref='details_commandes', lazy=True)
    client_final = db.relationship('ClientFinal', backref='details_commandes', lazy=True)
    destination = db.relationship('Destination', backref='details_commandes_dest', lazy=True) # Renommé backref

    # La relation 'missions' est définie via backref dans Mission (relationship secondary)
    # missions = db.relationship('Mission', secondary='mission_detail', back_populates='details_commandes', lazy='dynamic') # Pas besoin d'ajouter ceci, backref s'en charge.

    def __repr__(self):
        return f"<DetailCommande {self.id_detail_commande} (Qty: {self.quantite}) for Ref: {self.entete_commande.reference if self.entete_commande else 'N/A'}>"

    def to_dict(self):
        return {
            'id_detail_commande': self.id_detail_commande,
            'quantite': self.quantite,
            'description_colis': self.description_colis,
            'volume': float(self.volume) if self.volume else None,
            'poids': float(self.poids) if self.poids else None,
            'id_entete_commande': self.id_entete_commande,
            'entete_reference': self.entete_commande.reference if self.entete_commande else None,
            'id_type_vehicule': self.id_type_vehicule,
            'type_vehicule_nom': self.type_vehicule.nom_type if self.type_vehicule else None,
            'id_client_final': self.id_client_final,
            'client_final_nom': f"{self.client_final.nom} {self.client_final.prenom or ''}" if self.client_final else None,
            'id_destination': self.id_destination,
            'destination_description': self.destination.description if self.destination else None
            # 'missions_ids': [m.id_mission for m in self.missions.all()] # Pourrait être ajouté si utile
        }