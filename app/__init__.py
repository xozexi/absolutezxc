from flask import Flask, redirect, url_for
from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import SQLAlchemyUserDatastore, Security, current_user
# from app.models import Items, User, Role, roles_users, SiteBott, SiteText,UReview, Social_network, ChatMessage
from app.settings import app
from app.models import db, User, Role, Post, Comment, Like, Subscription
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot



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


# Определите кастомную вкладку
class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        # Создаем гистограмму для распределения уровней пользователей
        fig_level = px.histogram(db.session.query(User.level), nbins=5, title='Distribution of User Levels')
        graph_html_level = plot(fig_level, output_type='div')

        # Создаем круговую диаграмму для отображения активности пользователей (количество постов)
        fig_activity = px.pie(
            db.session.query(User.id, db.func.count(Post.id).label('post_count')).join(Post).group_by(User.id),
            names='id', values='post_count', title='User Activity')

        # Создаем Subplots (комбинированный график)
        fig_combined = make_subplots(rows=2, cols=2,
                                     subplot_titles=['User Levels', 'User Activity', 'User Experience Distribution',
                                                     'Comments per Post'])

        # Добавляем графики в Subplots
        fig_combined.add_trace(fig_level.data[0], row=1, col=1)

        # Круговая диаграмма (переработано с использованием Plotly Graph Objects)
        # Создаем круговую диаграмму для отображения активности пользователей (количество постов)

        # Создаем столбчатую диаграмму с использованием Plotly Express
        fig_bar = px.histogram(db.session.query(User.exp), nbins=3, title='Distribution of User Experience')
        graph_html_bar = plot(fig_bar, output_type='div')

        # Создаем круговую диаграмму для количества комментариев на каждый пост
        fig_pie = px.pie(db.session.query(Comment.post_id, db.func.count(Comment.id).label('comment_count')).group_by(
            Comment.post_id),
                         names='post_id', values='comment_count', title='Comments per Post')
        graph_html_pie = plot(fig_pie, output_type='div')

        # Обновляем Layout для лучшего отображения
        fig_combined.update_layout(height=700, showlegend=False)

        # Сохраняем график в формате HTML
        graph_html_combined = plot(fig_combined, output_type='div')


        return self.render('admin/diagrams.html', graph_html_level=graph_html_level,
                               graph_html_activity=graph_html_combined,
                               graph_html_bar=graph_html_bar, graph_html_pie=graph_html_pie, graph_html_combined=graph_html_combined)


admin = Admin(app, 'ADMIN', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(AnalyticsView(name='Analytics', endpoint='admin/analytics'))
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Role, db.session))
admin.add_view(AdminView(Post, db.session))
admin.add_view(AdminView(Comment, db.session))
admin.add_view(AdminView(Like, db.session))
admin.add_view(AdminView(Subscription, db.session))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
