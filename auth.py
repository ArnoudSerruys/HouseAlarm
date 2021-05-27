import sys
from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import login_required, current_user
from flask_security.utils import hash_password, login_user, logout_user, verify_and_update_password

from app import app, db, user_datastore

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        user_datastore.create_user(email=request.form.get('email'), name=request.form.get('name'), password=hash_password(request.form.get('password')))
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/login', methods=['POST','GET'])
def login():
    app.logger.setLevel(30)
    app.logger.info('entering login POST')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = user_datastore.get_user(email)

        if verify_and_update_password(password, user):
            login_user(user)
            return redirect(url_for('main.appmain',action='main'))
        else:
            return redirect(url_for('auth.login'))

    else:
        return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user(current_user)
    return render_template('logout.html', name=current_user.name)

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
