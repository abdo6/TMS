# import_geo_data.py
import sys
import os

# Ajouter le dossier parent (racine du projet) au PYTHONPATH
# pour que 'app' puisse être importé correctement
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models.ville import Ville
from app.models.province import Province

# --- Données à insérer ---
# Liste simplifiée de villes et provinces/préfectures du Maroc pour la démo.
# Dans ce modèle, une Province est associée à une Ville principale (son chef-lieu).
MOROCCAN_GEODATA = [
    {
        "code_ville": "CASA", "nom_ville": "Casablanca",
        "provinces_names": ["Casablanca-Anfa", "Ain Chock", "Hay Hassani", "Ben M'Sick", "Mohammedia", "Nouaceur"]
    },
    {
        "code_ville": "RAB", "nom_ville": "Rabat",
        "provinces_names": ["Rabat", "Salé", "Skhirate-Témara"]
    },
    {
        "code_ville": "MRK", "nom_ville": "Marrakech",
        "provinces_names": ["Marrakech", "Al Haouz", "Chichaoua", "Rehamna"]
    },
    {
        "code_ville": "FES", "nom_ville": "Fès",
        "provinces_names": ["Fès", "Moulay Yacoub", "Sefrou"]
    },
    {
        "code_ville": "TANG", "nom_ville": "Tanger",
        "provinces_names": ["Tanger-Assilah", "Fahs-Anjra", "Larache"]
    },
    {
        "code_ville": "AGAD", "nom_ville": "Agadir",
        "provinces_names": ["Agadir Ida-Ou Tanane", "Chtouka Ait Baha", "Taroudant"]
    }
]

def import_data():
    app = create_app()
    with app.app_context():
        print("\n--- Starting Geographic Data Import ---")
        
        # Dictionary to store Ville IDs for linking Provinces
        ville_ids = {}

        # 1. Insert Villes
        print("\nInserting Villes:")
        for ville_data in MOROCCAN_GEODATA:
            ville_code = ville_data['code_ville']
            ville_name = ville_data['nom_ville']

            existing_ville = db.session.execute(db.select(Ville).filter_by(code_ville=ville_code)).scalar_one_or_none()
            if existing_ville:
                print(f"  Ville '{ville_name}' (Code: {ville_code}) already exists. Skipping.")
                ville_ids[ville_name] = existing_ville.id_ville
            else:
                new_ville = Ville(code_ville=ville_code, nom_ville=ville_name)
                db.session.add(new_ville)
                # db.session.flush() is needed to get the ID for new_ville immediately before commit
                # but if all Villes are added and then committed, we can query them later.
                # For simplicity and robustness, we'll commit them first.
                db.session.flush() # IMPORTANT: get ID before commit for related objects
                ville_ids[ville_name] = new_ville.id_ville
                print(f"  Added Ville: {ville_name} (ID: {new_ville.id_ville})")
        
        db.session.commit() # Commit Villes first to ensure they have IDs
        print("Villes committed to database.")

        # Refresh ville_ids in case new ones were added and we need their IDs for provinces
        # This is safer if the script is run multiple times and some cities were already there.
        all_villes = db.session.execute(db.select(Ville)).scalars().all()
        for v in all_villes:
            ville_ids[v.nom_ville] = v.id_ville

        # 2. Insert Provinces
        print("\nInserting Provinces:")
        for ville_data in MOROCCAN_GEODATA:
            ville_name = ville_data['nom_ville'] # <-- CORRECTION ICI
            current_ville_id = ville_ids.get(ville_name)

            if current_ville_id is None:
                print(f"  Warning: Ville ID for '{ville_name}' not found. Cannot add its provinces.")
                continue

            for province_name in ville_data['provinces_names']:
                existing_province = db.session.execute(db.select(Province).filter_by(nom_province=province_name, id_ville=current_ville_id)).scalar_one_or_none()
                if existing_province:
                    print(f"  Province '{province_name}' for '{ville_name}' already exists. Skipping.")
                else:
                    new_province = Province(nom_province=province_name, id_ville=current_ville_id)
                    db.session.add(new_province)
                    print(f"  Added Province: {province_name} (for Ville: {ville_name}, ID: {current_ville_id})")
        
        db.session.commit() # Commit Provinces
        print("Provinces committed to database.")

        print("\n--- Geographic Data Import Finished Successfully ---")

if __name__ == '__main__':
    import_data()