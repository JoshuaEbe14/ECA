from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from app import login_manager

from models.forms import RegForm
from models.users import User
import os

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = User.getUser(email=form.email.data)
            if not existing_user:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                User.createUser(email=form.email.data,password=hashpass, name=form.name.data)
                return redirect(url_for('auth.login'))
            else:
                form.email.errors.append("User already existed")
                render_template('register.html', form=form, panel="Register")
    return render_template('register.html', form=form, panel="Register")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = RegForm()
    if request.method == 'POST':
        print(request.form.get('checkbox'))
        if form.validate():
            check_user = User.getUser(email=form.email.data)
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('packageController.packages'))      
                else:
                    form.password.errors.append("User Password Not Correct")
            else:
                form.email.errors.append("No Such User")
    return render_template('login.html', form=form, panel="Login")

@auth.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('packageController.packages'))

# Load the current user if any
@login_manager.user_loader
def load_user(user_id):
    print('loading user_id: ', user_id)
    return User.getUserById(user_id)





    

