# app/models/destination.py
from app import db

class Destination(db.Model):
    __tablename__ = 'destination'

    id_destination = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    description = db.Column(db.String(255))

    # Clés étrangères vers Ville et Province
    id_ville = db.Column(db.Integer, db.ForeignKey('ville.id_ville'))
    id_province = db.Column(db.Integer, db.ForeignKey('province.id_province'))

    # Relations avec les modèles Ville et Province
    ville = db.relationship('Ville', backref='destinations', lazy=True)
    province = db.relationship('Province', backref='destinations', lazy=True)

    # La ligne "missions = db.relationship(...)" est SUPPRIMÉE d'ici !
    # La relation bidirectionnelle est déjà gérée par la "backref" dans Mission.py
    # Mission.destination = db.relationship('Destination', backref='missions_as_main_dest', lazy=True)
    # Ce qui signifie que depuis une Destination, vous pouvez accéder à des missions via .missions_as_main_dest

    # La relation "missions" dans Mission.py faisait aussi un backref,
    # mais la ligne "missions = db.relationship('Mission', backref='destination', lazy=True)"
    # EST CELLE QUI CRÉE LE CONFLIT, car elle tente de créer un 'destination' sur Mission,
    # qui existe déjà.

    # Votre diagramme de classes montre 'Destination.missions'
    # Si vous voulez une liste directe de missions depuis une destination,
    # vous l'avez via 'missions_as_main_dest' (le backref de Mission.destination)
    # Donc, AUCUNE LIGNE SUPPLÉMENTAIRE n'est nécessaire ici pour cela.

    # Si vous avez une relation 'missions' ici qui est distincte (par exemple, pour des missions qui ont cette destination comme *n'importe quel* point de passage, et non seulement le principal),
    # il faudrait une table de liaison ou un champ spécifique dans Mission pour ça, et une définition différente.
    # Mais pour la structure actuelle, la suppression de cette ligne est la solution la plus simple et correcte.

    def __repr__(self):
        return f"<Destination {self.description or 'N/A'} (Lat: {self.latitude}, Long: {self.longitude})>"

    def to_dict(self):
        return {
            'id_destination': self.id_destination,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'description': self.description,
            'id_ville': self.id_ville,
            'ville_nom': self.ville.nom_ville if self.ville else None,
            'id_province': self.id_province,
            'province_nom': self.province.nom_province if self.province else None
        }