# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # debug=True est bon pour le développement (recharge auto, messages d'erreur détaillés)