# app/routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user # <-- Assurez-vous que current_user est bien là
from app.models.user import User
from app import db # Importez l'instance db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Si l'utilisateur est déjà connecté, le rediriger loin de la page de connexion
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

        if user and user.check_password(password):
            login_user(user) # Connecte l'utilisateur
            flash('Connexion réussie !', 'success')
            # Rediriger vers la page d'où l'utilisateur venait, ou vers l'accueil par défaut
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required # S'assurer que seul un utilisateur connecté peut se déconnecter
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))