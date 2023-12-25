from flask import Flask
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

UPLOAD_FOLDER = 'app/static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECURITY_PASSWORD_SALT'] = 'A*QLE*SJA*QKjsdjd86b8nnm0*'
app.config['SECRET_KEY'] = "A*QLE*SJA*QKjsdjd86b8nnm0*"
# socketio = SocketIO(app, cors_allowed_origins="*")
manager = LoginManager()
manager.init_app(app)
manager.session_protection = "strong"
login_serializer = URLSafeTimedSerializer(app.secret_key)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



