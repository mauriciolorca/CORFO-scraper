from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Application Factory
def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure random key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///splitwise.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    # Import and register blueprints
    from .routes.auth import auth as auth_blueprint
    from .routes.main import main as main_blueprint
    from .routes.groups import groups as groups_blueprint
    from .routes.expenses import expenses as expenses_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(groups_blueprint)
    app.register_blueprint(expenses_blueprint)

    return app
