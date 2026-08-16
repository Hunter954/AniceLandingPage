from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default='Administrador')
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(60), default='')
    role = db.Column(db.String(30), nullable=False, default='editor')
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        return bool(self.enabled)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    value = db.Column(db.Text, default='')
    kind = db.Column(db.String(30), default='text')
    label = db.Column(db.String(160), nullable=False)
    group = db.Column(db.String(80), default='Geral')
    sort_order = db.Column(db.Integer, default=0)


class ContentItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(80), index=True, nullable=False)
    title = db.Column(db.String(220), nullable=False)
    subtitle = db.Column(db.String(255), default='')
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(255), default='')
    icon = db.Column(db.String(120), default='bi-star')
    date_text = db.Column(db.String(80), default='')
    location = db.Column(db.String(180), default='')
    link_text = db.Column(db.String(100), default='Saiba mais')
    link_url = db.Column(db.String(255), default='#')
    extra = db.Column(db.Text, default='')
    sort_order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    phone = db.Column(db.String(60), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @property
    def created_at_br(self):
        return self.created_at - timedelta(hours=3) if self.created_at else None
