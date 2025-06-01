# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime # Importé pour current_year dans le context processor


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Charger la configuration depuis app.config.settings
    # Cela suppose que vous avez un dossier app/config/ et un fichier settings.py dedans.
    # Et que app/config/ a un fichier __init__.py (même vide) pour être un module.
    try:
        app.config.from_object('app.config.settings')
    except ImportError:
        # Fallback si app.config.settings n'est pas trouvable comme module python
        # (par exemple si app/config/__init__.py manque ou si la structure est différente)
        # Essayez un chemin relatif si settings.py est directement dans config/ au même niveau que app/
        # Mais la méthode from_object est généralement plus propre.
        # Pour votre structure app/config/settings.py, from_object est la bonne voie.
        # Si from_object échoue, vérifiez que app/config/__init__.py existe.
        app.config.from_pyfile('config/settings.py', silent=True) # Essaie de charger depuis un dossier config/ au niveau de app/
        # Le 'silent=True' peut masquer l'erreur si le fichier n'est pas trouvé par from_pyfile,
        # il est donc préférable que from_object fonctionne.

    # Vérifier si la configuration essentielle est chargée
    if not app.config.get('SECRET_KEY') or not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError("Configuration essentielle (SECRET_KEY ou SQLALCHEMY_DATABASE_URI) manquante. Vérifiez settings.py.")

    db.init_app(app)
    migrate.init_app(app, db) # Initialiser Flask-Migrate
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Nom du blueprint 'auth' et de la route 'login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"

    # Import des modèles (doit être fait après l'initialisation de db et migrate)
    # et avant l'enregistrement des blueprints si les blueprints utilisent les modèles.
    from app.models import user, client_initial, chauffeur, vehicule, mission, ville, province, destination
    from app.models import service_client, type_vehicule, entete_commande, client_final, detail_commande
    from app.models import trajet, sous_traitant, type_indispo_chauffeur, type_indispo_vehicule
    from app.models import indispo_chauffeur, indispo_vehicule, vehicule_externe, chauffeur_externe
    from app.models import mission_detail, date_cv, date_tr, affretement, feuille_de_route
    from app.models import localisation
    
    # Enregistrement des blueprints
    from .routes.main_routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.auth_routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth') # url_prefix est une bonne pratique pour les routes d'auth



    from .routes.api_routes import api as api_blueprint # <--- AJOUTEZ CETTE LIGNE
    app.register_blueprint(api_blueprint, url_prefix='/api') # <--- AJOUTEZ CETTE LIGNE avec un préfixe URL

        # Dans app/__init__.py

    # ... (autres imports et code) ...
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User # <--- AJOUTER CET IMPORT SPÉCIFIQUE ICI
        return db.session.get(User, int(user_id)) 

    # Context processor pour rendre ROLES et current_year disponibles dans tous les templates
    @app.context_processor
    def inject_global_vars_for_templates():
        # ROLES doit être importé ici ou accessible globalement
        from app.models.user import ROLES 
        return dict(
            ROLES=ROLES,
            current_year=datetime.utcnow().year,
            now=datetime.utcnow
            
        )

    return app
    