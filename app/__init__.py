from flask import Flask, redirect, url_for
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import SQLAlchemyUserDatastore, Security, current_user
# from app.models import Items, User, Role, roles_users, SiteBott, SiteText,UReview, Social_network, ChatMessage
from app.settings import app
from app.models import db, User, Role, Post, Comment, Like


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


admin = Admin(app, 'ADMIN', url='/', index_view=HomeAdminView())
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Role, db.session))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)