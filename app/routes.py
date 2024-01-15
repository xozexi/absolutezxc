import os
import shutil
import re
from urllib.parse import urlparse, urljoin
from functools import wraps
from flask import render_template, redirect, url_for, request, flash, session
from flask_security import LoginForm
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
# from flask_login import login_user, login_required, logout_user, current_user
# from flask_socketio import SocketIO, send, join_room

# from app import defs, user_datastore
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

from app.settings import app
from flask_login import login_user, current_user, logout_user, login_required
from app.models import db, User, Role, Post, Comment, Like


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])  # define login page path
def login():  # define login page fucntion

    if request.method == 'GET':  # if the request is a GET we return the login page
        return render_template('security/login_user.html')
    else:
        print("login")
        username = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        print(f"Авторизация пользователя {username}")
        if not user:
            flash('Неверный логин!')
            return redirect(url_for('login'))
        elif user.password != password:
            flash('Неверный пароль!')
            return redirect(url_for('login'))  # if the user doesn't exist or password is wrong, reload the page
        # if the above check passes, then we know the user has the right credentials
        print(f"login {user.username} {user.password} {user.level} {user.exp} {user.active}")
        login_user(user, remember=True)
        print(f"{current_user.is_authenticated} {current_user.is_active}")
        if current_user.is_authenticated:
            print(current_user.username)
            return redirect(url_for('index'))
        else:
            flash('Ошибка авторизации!')
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    # Проверка, если пользователь уже аутентифицирован, перенаправить его на главную страницу
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    print(f"Регистрация пользователя {request.form.get('username')}")
    if request.method == 'POST':
        if User.query.filter_by(username=request.form.get('login')).first():
            flash('Пользователь с таким логином уже существует')
            return redirect(url_for('register'))
        if request.form.get('password') != request.form.get('rpassword'):
            flash('Пароли не совпадают')
            return redirect(url_for('register'))
        # Создание нового пользователя
        user = User(username=request.form.get('login'), password=request.form.get('password'))
        # Получение роли из базы данных
        role = Role.query.get(2)

        # Если роль существует, установите ее для пользователя
        if role:
            user.roles.append(role)
        # Добавление пользователя в базу данных
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(f"Ошибка при добавлении пользователя в базу данных: {e}")
            flash('Ошибка при добавлении пользователя в базу данных.\nВозможно такой пользователь уже существует.')

        flash('Регистрация успешна. Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Выход с аккаунта!', 'успешно')
    return redirect(url_for('index'))


@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

# Пример другого маршрута
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/user/<string:username>')
@login_required
def get_user(username):
    # Здесь вы можете использовать user_id для получения информации о пользователе из базы данных или других источников данных
    # return f'User ID: {user_id}'
    return render_template('user_profile.html', username=username)