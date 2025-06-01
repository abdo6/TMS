# app/models/mission_detail.py
from app import db
from sqlalchemy.orm import relationship # Ajoutez cet import si ce n'est pas déjà fait

class MissionDetail(db.Model):
    __tablename__ = 'mission_detail'

    id_mission = db.Column(db.Integer, db.ForeignKey('mission.id_mission'), primary_key=True)
    id_detail_commande = db.Column(db.Integer, db.ForeignKey('detail_commande.id_detail_commande'), primary_key=True)
    
    ordre_livraison = db.Column(db.Integer) 

    # Relations bidirectionnelles
    # Utiliser back_populates est généralement plus explicite, mais pour rester simple avec backref:
    # La warning indique un chevauchement entre MissionDetail.mission et Mission.details_commandes (et DetailCommande.missions)
    # et MissionDetail.detail_commande et Mission.details_commandes (et DetailCommande.missions)
    # Les noms dans overlaps doivent correspondre aux noms des *relations* qui se chevauchent.
    # Dans Mission.py, la relation s'appelle 'details_commandes'.
    # Dans DetailCommande.py, la relation inverse s'appelle 'missions'.

    mission = db.relationship('Mission', 
                              backref=db.backref('mission_details_link', cascade="all, delete-orphan", lazy=True), 
                              overlaps="details_commandes,missions_affectees") # <--- AJOUTÉ overlaps ICI
    
    detail_commande = db.relationship('DetailCommande', 
                                     backref=db.backref('mission_details_link_reverse', cascade="all, delete-orphan", lazy=True), # Renommé backref pour éviter conflit
                                     overlaps="missions,details_commandes_rel") # <--- AJOUTÉ overlaps ICI

    def __repr__(self):
        return f"<MissionDetail Mission ID: {self.id_mission}, DetailCommande ID: {self.id_detail_commande}>"

    def to_dict(self):
        return {
            'id_mission': self.id_mission,
            'id_detail_commande': self.id_detail_commande,
            'ordre_livraison': self.ordre_livraison,
        }