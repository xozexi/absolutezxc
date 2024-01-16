import os
import shutil
import re
from datetime import time
from urllib.parse import urlparse, urljoin
from functools import wraps
from flask import render_template, redirect, url_for, request, flash, session, jsonify
from flask_security import LoginForm
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
# from flask_login import login_user, login_required, logout_user, current_user
# from flask_socketio import SocketIO, send, join_room
import datetime
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


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            post = Post(title=title, content=content, user_id=current_user.id, pub_date=datetime.datetime.now())
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('get_user', username=current_user.username))
        except Exception as e:
            flash("Ошибка при добавлении поста")
            print(e)
            return redirect(url_for('add_post'))
    else:
        return render_template('new_post.html')


@app.route('/user/<string:username>')
@login_required
def get_user(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.id.desc()).all()

    likes = {}
    for post in posts:
        liked_by_user = False
        print(Like.query.filter_by(user_id=current_user.id, post_id=post.id).first())
        if Like.query.filter_by(user_id=current_user.id, post_id=post.id).first():
            liked_by_user = True
        likes[post.id] = {
            'count': get_post_likes(post.id),
            'liked_by_user': liked_by_user
        }
        print(likes[post.id])

    return render_template('user_profile.html', User=user, Posts=posts, Likes=likes)


@app.route('/like_post/<int:post_id>/')
@login_required
def like_post(post_id):
    try:
        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if existing_like:
            db.session.delete(existing_like)
            is_like_set = False
            User.query.get(Post.query.get(post_id).user_id).exp -= 1
        else:
            new_like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(new_like)
            is_like_set = True
            User.query.get(Post.query.get(post_id).user_id).exp += 1

        db.session.commit()

        # Получаем новое количество лайков
        updated_likes_count = Like.query.filter_by(post_id=post_id).count()

        return jsonify({'likes_count': updated_likes_count, 'is_like_set': is_like_set}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return '', 500


@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
@login_required
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('comments.html', Users=User, Comments=comments, post_id=post_id)


@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        new_comment = Comment(text=request.form.get('text_comm'),
                              user_id=current_user.id,
                              post_id=post_id,
                              pub_date=datetime.datetime.now())
        db.session.add(new_comment)
        db.session.commit()
        flash("")
        return render_template(url_for('get_comments', post_id=post_id))
    except:
        flash("Ошибка при добавлении комментария")
        return redirect(url_for('get_comments', post_id=post_id))


@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('get_comments', post_id=comment.post_id))
    except:
        flash("Ошибка при удалении комментария")
        return redirect(url_for('get_comments', post_id=comment.post_id))


@app.route('/get_exp', methods=['GET'])
def get_exp():
    try:
        # Получаем id пользователя из запроса
        user_id = request.args.get('userId')

        # Находим пользователя по id в базе данных
        user = User.query.get(user_id)

        # Возвращаем значение exp в формате JSON
        print(user.exp)
        return jsonify({'exp': user.exp})
    except Exception as e:
        return jsonify({'error': str(e)})


def get_post_likes(post_id):
    try:
        post_likes = Like.query.filter_by(post_id=post_id).count()
        return post_likes
    except Exception as e:
        return -1
