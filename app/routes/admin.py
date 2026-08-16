import os, uuid, secrets, string
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from .. import db
from ..models import AdminUser, SiteSetting, ContentItem, ContactMessage

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')
ALLOWED = {'png','jpg','jpeg','webp','gif','svg','ico'}
ROLES = {'admin': 'Administrador', 'editor': 'Editor'}

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Você não tem permissão para acessar esta área.', 'warning')
            return redirect(url_for('admin.dashboard'))
        return view(*args, **kwargs)
    return wrapped

def generate_temp_password(length=14):
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password) and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password) and any(c in '!@#$%&*' for c in password)):
            return password

SECTIONS = {
 'stats':'Números e destaques','areas':'Eixos de atuação','projects':'Projetos e propostas','gallery':'Galeria','blog':'Blog / Notícias'
}

@admin_bp.app_context_processor
def inject_admin_message_count():
    return {'admin_unread_messages': ContactMessage.query.filter_by(is_read=False).count()}

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
            if not user.enabled:
                flash('Este usuário está desativado. Procure um administrador.', 'warning')
                return render_template('admin/login.html')
            user.last_login_at = datetime.utcnow()
            db.session.commit()
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
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    total_messages = ContactMessage.query.count()
    return render_template('admin/dashboard.html', counts=counts, sections=SECTIONS, unread_messages=unread_messages, total_messages=total_messages)

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


@admin_bp.route('/blog/upload-image', methods=['POST'])
@login_required
def blog_upload_image():
    file = request.files.get('image')
    if not file or not file.filename:
        return jsonify({'ok': False, 'error': 'Nenhuma imagem enviada.'}), 400
    try:
        filename = save_file(file)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    return jsonify({'ok': True, 'url': url_for('site.uploads', filename=filename)})

@admin_bp.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        duplicate = AdminUser.query.filter(AdminUser.email == email, AdminUser.id != current_user.id).first()
        if not name or not email:
            flash('Nome e e-mail são obrigatórios.', 'danger')
        elif duplicate:
            flash('Já existe um usuário cadastrado com este e-mail.', 'danger')
        else:
            current_user.name = name
            current_user.email = email
            current_user.phone = request.form.get('phone','').strip()
            if request.form.get('password'):
                current_user.set_password(request.form['password'])
            db.session.commit(); flash('Perfil atualizado.','success')
            return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html', sections=SECTIONS)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    q = request.args.get('q','').strip()
    status = request.args.get('status','all')
    role = request.args.get('role','all')
    query = AdminUser.query
    if q:
        like = f'%{q}%'
        query = query.filter(or_(AdminUser.name.ilike(like), AdminUser.email.ilike(like), AdminUser.phone.ilike(like)))
    if status == 'active': query = query.filter_by(enabled=True)
    elif status == 'inactive': query = query.filter_by(enabled=False)
    if role in ROLES: query = query.filter_by(role=role)
    items = query.order_by(AdminUser.enabled.desc(), AdminUser.name.asc()).all()
    stats = {
        'total': AdminUser.query.count(),
        'active': AdminUser.query.filter_by(enabled=True).count(),
        'admins': AdminUser.query.filter_by(role='admin', enabled=True).count(),
    }
    return render_template('admin/users.html', items=items, roles=ROLES, stats=stats, q=q, status=status, role=role, sections=SECTIONS)


@admin_bp.route('/users/new', methods=['GET','POST'])
@login_required
@admin_required
def user_new():
    generated_password = generate_temp_password()
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        role = request.form.get('role','editor')
        if role not in ROLES: role = 'editor'
        if not name or not email or not password:
            flash('Preencha nome, e-mail e senha.', 'danger')
            generated_password = password or generated_password
        elif len(password) < 8:
            flash('A senha precisa ter pelo menos 8 caracteres.', 'danger')
            generated_password = password
        elif AdminUser.query.filter_by(email=email).first():
            flash('Já existe um usuário com este e-mail.', 'danger')
            generated_password = password
        else:
            user = AdminUser(name=name, email=email, phone=request.form.get('phone','').strip(), role=role, enabled=bool(request.form.get('enabled')))
            user.set_password(password)
            db.session.add(user); db.session.commit()
            flash(f'Usuário {name} criado com sucesso.', 'success')
            return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', user=None, roles=ROLES, generated_password=generated_password, sections=SECTIONS)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET','POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = AdminUser.query.get_or_404(user_id)
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        role = request.form.get('role','editor')
        enabled = bool(request.form.get('enabled'))
        duplicate = AdminUser.query.filter(AdminUser.email == email, AdminUser.id != user.id).first()
        if not name or not email:
            flash('Nome e e-mail são obrigatórios.', 'danger')
        elif duplicate:
            flash('Já existe um usuário com este e-mail.', 'danger')
        elif user.id == current_user.id and (not enabled or role != 'admin'):
            flash('Você não pode desativar nem remover o próprio acesso de administrador.', 'warning')
        else:
            if role not in ROLES: role = 'editor'
            # Garante que sempre exista ao menos um administrador ativo.
            if user.role == 'admin' and user.enabled and (role != 'admin' or not enabled):
                other_admins = AdminUser.query.filter(AdminUser.id != user.id, AdminUser.role == 'admin', AdminUser.enabled.is_(True)).count()
                if other_admins == 0:
                    flash('É necessário manter pelo menos um administrador ativo.', 'warning')
                    return render_template('admin/user_form.html', user=user, roles=ROLES, generated_password='', sections=SECTIONS)
            user.name, user.email = name, email
            user.phone = request.form.get('phone','').strip()
            user.role, user.enabled = role, enabled
            password = request.form.get('password','')
            if password:
                if len(password) < 8:
                    flash('A nova senha precisa ter pelo menos 8 caracteres.', 'danger')
                    return render_template('admin/user_form.html', user=user, roles=ROLES, generated_password=password, sections=SECTIONS)
                user.set_password(password)
            db.session.commit(); flash('Usuário atualizado com sucesso.', 'success')
            return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', user=user, roles=ROLES, generated_password='', sections=SECTIONS)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def user_toggle(user_id):
    user = AdminUser.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode desativar o próprio usuário.', 'warning')
    elif user.role == 'admin' and user.enabled and AdminUser.query.filter_by(role='admin', enabled=True).count() <= 1:
        flash('É necessário manter pelo menos um administrador ativo.', 'warning')
    else:
        user.enabled = not user.enabled; db.session.commit()
        flash('Status do usuário atualizado.', 'success')
    return redirect(request.referrer or url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = AdminUser.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode excluir o próprio usuário.', 'warning')
    elif user.role == 'admin' and AdminUser.query.filter_by(role='admin').count() <= 1:
        flash('É necessário manter pelo menos um administrador.', 'warning')
    else:
        name = user.name; db.session.delete(user); db.session.commit(); flash(f'Usuário {name} excluído.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/messages')
@login_required
def messages():
    status = request.args.get('status', 'all')
    query = ContactMessage.query
    if status == 'unread':
        query = query.filter_by(is_read=False)
    elif status == 'read':
        query = query.filter_by(is_read=True)
    items = query.order_by(ContactMessage.created_at.desc()).all()
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    return render_template('admin/messages.html', items=items, status=status, unread_count=unread_count, sections=SECTIONS)


@admin_bp.route('/messages/<int:message_id>')
@login_required
def message_view(message_id):
    item = ContactMessage.query.get_or_404(message_id)
    if not item.is_read:
        item.is_read = True
        db.session.commit()
    return render_template('admin/message_view.html', item=item, sections=SECTIONS)


@admin_bp.route('/messages/<int:message_id>/toggle-read', methods=['POST'])
@login_required
def message_toggle_read(message_id):
    item = ContactMessage.query.get_or_404(message_id)
    item.is_read = not item.is_read
    db.session.commit()
    flash('Status da mensagem atualizado.', 'success')
    return redirect(request.referrer or url_for('admin.messages'))


@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def message_delete(message_id):
    item = ContactMessage.query.get_or_404(message_id)
    db.session.delete(item)
    db.session.commit()
    flash('Mensagem excluída.', 'success')
    return redirect(url_for('admin.messages'))
