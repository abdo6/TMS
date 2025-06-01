# app/models/affretement.py
from app import db
from datetime import datetime, date

class Affretement(db.Model):
    __tablename__ = 'affretement'

    id_affretement = db.Column(db.Integer, primary_key=True)
    date_demande = db.Column(db.Date, nullable=False, default=date.today())
    date_debut_souhaitee = db.Column(db.Date, nullable=False)
    date_fin_souhaitee = db.Column(db.Date, nullable=False)
    description_besoin = db.Column(db.String(500), nullable=False)
    statut = db.Column(db.String(50), default='En attente', nullable=False) # Ex: 'En attente', 'Confirmé', 'Annulé', 'En cours', 'Terminé'
    cout_estime = db.Column(db.Numeric(10, 2)) # Coût estimé de l'affrètement

    # Clés étrangères
    # Un affrètement peut être lié à un DetailCommande (pour quelle livraison)
    id_detail_commande = db.Column(db.Integer, db.ForeignKey('detail_commande.id_detail_commande')) # Optionnel au début
    # Un affrètement est réalisé par un SousTraitant
    id_sous_traitant = db.Column(db.Integer, db.ForeignKey('sous_traitant.id_sous_traitant')) # Peut être NULL si encore 'En attente' de sélection
    # Si un véhicule et un chauffeur spécifiques sont assignés par le sous-traitant
    id_vehicule_externe = db.Column(db.Integer, db.ForeignKey('vehicule_externe.id_vehicule_externe')) # Optionnel
    id_chauffeur_externe = db.Column(db.Integer, db.ForeignKey('chauffeur_externe.id_chauffeur_externe')) # Optionnel

    # Relations
    detail_commande = db.relationship('DetailCommande', backref='affretements', lazy=True)
    sous_traitant = db.relationship('SousTraitant', backref='affretements', lazy=True)
    vehicule_externe = db.relationship('VehiculeExterne', backref='affretements', lazy=True)
    chauffeur_externe = db.relationship('ChauffeurExterne', backref='affretements', lazy=True)

    def __repr__(self):
        return f"<Affretement {self.id_affretement} - {self.statut} pour {self.description_besoin}>"

    def to_dict(self):
        return {
            'id_affretement': self.id_affretement,
            'date_demande': self.date_demande.isoformat(),
            'date_debut_souhaitee': self.date_debut_souhaitee.isoformat(),
            'date_fin_souhaitee': self.date_fin_souhaitee.isoformat(),
            'description_besoin': self.description_besoin,
            'statut': self.statut,
            'cout_estime': float(self.cout_estime) if self.cout_estime else None,
            'id_detail_commande': self.id_detail_commande,
            'detail_commande_ref': self.detail_commande.entete_commande.reference if self.detail_commande and self.detail_commande.entete_commande else 'N/A',
            'id_sous_traitant': self.id_sous_traitant,
            'sous_traitant_nom': self.sous_traitant.nom_entreprise if self.sous_traitant else 'N/A',
            'id_vehicule_externe': self.id_vehicule_externe,
            'vehicule_externe_immat': self.vehicule_externe.immatriculation_ve if self.vehicule_externe else 'N/A',
            'id_chauffeur_externe': self.id_chauffeur_externe,
            'chauffeur_externe_nom': f"{self.chauffeur_externe.nom} {self.chauffeur_externe.prenom}" if self.chauffeur_externe else 'N/A'
        }