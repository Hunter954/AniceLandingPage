from flask import Blueprint, render_template, current_app, send_from_directory, abort, request, redirect, url_for, flash
from .. import db
from ..models import SiteSetting, ContentItem, ContactMessage

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
    blog_posts = ContentItem.query.filter_by(section='blog', active=True).order_by(ContentItem.created_at.desc(), ContentItem.id.desc()).limit(3).all()
    return render_template('site/index.html', blog_posts=blog_posts, **sections)

@site_bp.route('/blog')
def blog():
    posts = ContentItem.query.filter_by(section='blog', active=True).order_by(ContentItem.created_at.desc(), ContentItem.id.desc()).all()
    return render_template('site/blog.html', posts=posts)

@site_bp.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = ContentItem.query.filter_by(id=post_id, section='blog', active=True).first()
    if not post:
        abort(404)
    return render_template('site/blog_post.html', post=post)


@site_bp.route('/contato/enviar', methods=['POST'])
def contact_submit():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()
    website = request.form.get('website', '').strip()  # honeypot anti-spam

    if website:
        return redirect(url_for('site.home', _anchor='mensagem'))

    if not all([name, email, phone, message]):
        flash('Preencha nome, e-mail, telefone e mensagem.', 'danger')
        return redirect(url_for('site.home', _anchor='mensagem'))

    if len(name) > 160 or len(email) > 180 or len(phone) > 60 or len(message) > 5000:
        flash('Revise os dados enviados. A mensagem está acima do tamanho permitido.', 'danger')
        return redirect(url_for('site.home', _anchor='mensagem'))

    contact = ContactMessage(name=name, email=email, phone=phone, message=message)
    db.session.add(contact)
    db.session.commit()
    flash('Mensagem enviada com sucesso! Obrigado por entrar em contato.', 'success')
    return redirect(url_for('site.home', _anchor='mensagem'))

@site_bp.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
