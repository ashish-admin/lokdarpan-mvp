import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    # We pass instance_relative_config=True to make the app aware of its instance folder
    app = Flask(__name__, instance_relative_config=True) 
    
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["https://lokdarpan.netlify.app", "http://localhost:5173"]
        }
    })

    app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change'
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    
    # The database path will now be relative to the 'instance' folder, which is standard practice
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)
        
        from . import models

        return app