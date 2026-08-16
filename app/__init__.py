import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Faça login para acessar o painel.'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-change-me')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join(app.root_path, '..', 'uploads'))
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import AdminUser
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(AdminUser, int(user_id))

    from .routes.site import site_bp
    from .routes.admin import admin_bp
    app.register_blueprint(site_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        # Migração leve para instalações existentes (SQLite/PostgreSQL).
        # create_all não adiciona novas colunas em tabelas já criadas.
        columns = {c['name'] for c in inspect(db.engine).get_columns('admin_user')}
        additions = {
            'phone': "VARCHAR(60) DEFAULT ''",
            'role': "VARCHAR(30) NOT NULL DEFAULT 'editor'",
            'enabled': "BOOLEAN NOT NULL DEFAULT TRUE",
            'updated_at': "DATETIME",
            'last_login_at': "DATETIME",
        }
        if db.engine.dialect.name == 'postgresql':
            additions['updated_at'] = 'TIMESTAMP'
            additions['last_login_at'] = 'TIMESTAMP'
        for name, ddl in additions.items():
            if name not in columns:
                db.session.execute(text(f'ALTER TABLE admin_user ADD COLUMN {name} {ddl}'))
        db.session.commit()
        from .seed import seed_database
        seed_database()

    return app
