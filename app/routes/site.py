from flask import Blueprint, render_template, current_app, send_from_directory
from ..models import SiteSetting, ContentItem

site_bp = Blueprint('site', __name__)

@site_bp.app_context_processor
def inject_site_data():
    settings = {s.key: s.value for s in SiteSetting.query.all()}
    return {'settings': settings}

@site_bp.route('/')
def home():
    sections = {}
    for name in ['stats','areas','projects','gallery']:
        sections[name] = ContentItem.query.filter_by(section=name, active=True).order_by(ContentItem.sort_order, ContentItem.id).all()
    return render_template('site/index.html', **sections)

@site_bp.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
