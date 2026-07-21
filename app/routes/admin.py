import os, uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from .. import db
from ..models import AdminUser, SiteSetting, ContentItem

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')
ALLOWED = {'png','jpg','jpeg','webp','gif','svg','ico'}
SECTIONS = {
 'stats':'Números e resultados','areas':'Áreas de atuação','projects':'Projetos e propostas','news':'Notícias','gallery':'Galeria','agenda':'Agenda','testimonials':'Depoimentos'
}

def save_file(file):
    if not file or not file.filename: return ''
    ext = file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED: raise ValueError('Formato de imagem não permitido.')
    name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], name))
    return name

@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('admin.dashboard'))
    if request.method=='POST':
        user = AdminUser.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if user and user.check_password(request.form.get('password','')):
            login_user(user); return redirect(url_for('admin.dashboard'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    counts = {k: ContentItem.query.filter_by(section=k).count() for k in SECTIONS}
    return render_template('admin/dashboard.html', counts=counts, sections=SECTIONS)

@admin_bp.route('/settings/<group>', methods=['GET','POST'])
@login_required
def settings(group):
    items = SiteSetting.query.filter_by(group=group).order_by(SiteSetting.sort_order).all()
    if request.method=='POST':
        for item in items:
            if item.kind=='image':
                file = request.files.get(item.key)
                if file and file.filename:
                    try: item.value = save_file(file)
                    except ValueError as e: flash(str(e),'danger')
            else:
                item.value = request.form.get(item.key,'')
        db.session.commit(); flash('Informações atualizadas com sucesso.','success')
        return redirect(url_for('admin.settings', group=group))
    return render_template('admin/settings.html', items=items, group=group, sections=SECTIONS)

@admin_bp.route('/section/<section>')
@login_required
def section_list(section):
    if section not in SECTIONS: return redirect(url_for('admin.dashboard'))
    items = ContentItem.query.filter_by(section=section).order_by(ContentItem.sort_order, ContentItem.id).all()
    return render_template('admin/section_list.html', items=items, section=section, section_name=SECTIONS[section], sections=SECTIONS)

@admin_bp.route('/section/<section>/new', methods=['GET','POST'])
@login_required
def section_new(section):
    if section not in SECTIONS: return redirect(url_for('admin.dashboard'))
    item = ContentItem(section=section, sort_order=ContentItem.query.filter_by(section=section).count())
    if request.method=='POST':
        populate_item(item); db.session.add(item); db.session.commit(); flash('Item criado.','success')
        return redirect(url_for('admin.section_list',section=section))
    return render_template('admin/item_form.html', item=item, section=section, section_name=SECTIONS[section], sections=SECTIONS)

@admin_bp.route('/section/<section>/<int:item_id>/edit', methods=['GET','POST'])
@login_required
def section_edit(section,item_id):
    item = ContentItem.query.get_or_404(item_id)
    if request.method=='POST':
        populate_item(item); db.session.commit(); flash('Item atualizado.','success')
        return redirect(url_for('admin.section_list',section=section))
    return render_template('admin/item_form.html', item=item, section=section, section_name=SECTIONS.get(section,section), sections=SECTIONS)

@admin_bp.route('/section/<section>/<int:item_id>/delete', methods=['POST'])
@login_required
def section_delete(section,item_id):
    item = ContentItem.query.get_or_404(item_id); db.session.delete(item); db.session.commit(); flash('Item excluído.','success')
    return redirect(url_for('admin.section_list',section=section))

def populate_item(item):
    for field in ['title','subtitle','description','icon','date_text','location','link_text','link_url','extra']:
        setattr(item, field, request.form.get(field,''))
    item.sort_order = int(request.form.get('sort_order') or 0)
    item.active = bool(request.form.get('active'))
    file = request.files.get('image')
    if file and file.filename: item.image = save_file(file)

@admin_bp.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        current_user.name=request.form.get('name',current_user.name)
        current_user.email=request.form.get('email',current_user.email).lower()
        if request.form.get('password'): current_user.set_password(request.form['password'])
        db.session.commit(); flash('Perfil atualizado.','success')
    return render_template('admin/profile.html', sections=SECTIONS)
