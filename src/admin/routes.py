
import os
import secrets
import io
import pandas as pd
from flask import render_template, redirect, url_for, flash, request, current_app, send_file, session
from flask_login import login_required, current_user
from sqlalchemy import func
from src import db
from src.admin import bp
from src.admin.forms import (
    FileUploadForm, ElectionPeriodForm, CandidateListForm,
    AddCandidateForm, EditCandidateForm, VoterForm, DignityForm, EditUserForm,
    CreateUserForm
)
from src.models import Voter, ElectionPeriod, CandidateList, Candidate, User, Vote, AuditLog, Dignity
from src.utils import load_voters_from_excel
from werkzeug.utils import secure_filename
from src.decorators import admin_required, superadmin_required
from flask_login import login_user

def save_picture(form_picture, subfolder='profile_pics'):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('src/static/uploads', subfolder, picture_fn)

    output_dir = os.path.dirname(picture_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    form_picture.save(picture_path)

    return f"uploads/{subfolder}/{picture_fn}"

@bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/<int:period_id>/upload_voters', methods=['POST'])
@login_required
@admin_required
def upload_voters(period_id):
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join('src/static/uploads', filename)
        file.save(filepath)
        try:
            load_voters_from_excel(filepath, period_id)
            flash('Votantes cargados correctamente!', 'success')
        except Exception as e:
            flash(f'Ocurrió un error: {e}', 'danger')
    else:
        flash('Error al subir el archivo.', 'danger')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/election_periods')
@login_required
@admin_required
def list_election_periods():
    periods = ElectionPeriod.query.all()
    return render_template('admin/list_election_periods.html', periods=periods)

@bp.route('/election_periods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_election_period():
    form = ElectionPeriodForm()
    if form.validate_on_submit():
        new_period = ElectionPeriod(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(new_period)
        db.session.flush()
        
        blanco = CandidateList(name="Voto en Blanco", election_period_id=new_period.id)
        nulo = CandidateList(name="Voto Nulo", election_period_id=new_period.id)
        db.session.add(blanco)
        db.session.add(nulo)
        
        audit = AuditLog(user_id=current_user.id, action=f"Creado periodo electoral: {new_period.name}")
        db.session.add(audit)
        db.session.commit()
        flash('¡Nuevo periodo electoral creado con Voto Blanco y Nulo automáticos!', 'success')
        return redirect(url_for('admin.list_election_periods'))
    return render_template('admin/add_election_period.html', form=form)

@bp.route('/election_periods/<int:period_id>', methods=['GET'])
@login_required
@admin_required
def manage_election_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    list_form = CandidateListForm()
    voter_form = FileUploadForm()
    dignity_form = DignityForm()

    search_query = request.args.get('search', '').strip()
    all_voters = period.voters
    
    if search_query:
        sq_lower = search_query.lower()
        voters_to_display = [v for v in all_voters if 
                             sq_lower in v.cedula.lower() or 
                             sq_lower in v.name.lower() or 
                             sq_lower in v.lastname.lower()]
    else:
        voters_to_display = all_voters
    total_voters = len(voters_to_display)
    voters_to_display = voters_to_display[:20]

    dignities = period.dignities.all()

    return render_template('admin/manage_election_period.html', 
                           period=period, 
                           list_form=list_form, 
                           voter_form=voter_form,
                           dignity_form=dignity_form,
                           voters=voters_to_display,
                           total_voters=total_voters,
                           dignities=dignities)

@bp.route('/election_periods/<int:period_id>/dignities/add', methods=['POST'])
@login_required
@admin_required
def add_dignity(period_id):
    form = DignityForm()
    if form.validate_on_submit():
        new_dignity = Dignity(name=form.name.data, election_period_id=period_id)
        db.session.add(new_dignity)
        db.session.commit()
        flash('Nueva dignidad añadida.', 'success')
    else:
        flash('Error al añadir dignidad.', 'danger')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/dignities/<int:dignity_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_dignity(dignity_id):
    dignity = Dignity.query.get_or_404(dignity_id)
    period_id = dignity.election_period_id
    db.session.delete(dignity)
    db.session.commit()
    flash('Dignidad eliminada.', 'success')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/download_voter_template')
@login_required
@admin_required
def download_voter_template():
    file_path = os.path.join(current_app.root_path, 'static', 'downloads', 'plantilla_votantes.xlsx')
    return send_file(
        file_path, 
        as_attachment=True, 
        download_name='plantilla_votantes.xlsx', 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/election_periods/<int:period_id>/download_roll')
@login_required
@admin_required
def download_election_roll(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    voters = period.voters
    
    data = []
    for v in voters:
        data.append({
            'CÉDULA': v.cedula,
            'NOMBRES': v.name,
            'APELLIDOS': v.lastname
        })
    
    df = pd.DataFrame(data)
    
    # Crear un buffer en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Padron')
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'padron_periodo_{period.name}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/voters/<int:voter_id>/period/<int:period_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_voter_from_period(voter_id, period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    voter = Voter.query.get_or_404(voter_id)
    if voter in period.voters:
        period.voters.remove(voter)
        db.session.commit()
        flash(f'El votante {voter.name} {voter.lastname} ha sido removido del periodo.', 'success')
    else:
        flash('El votante no se encuentra en este periodo electoral.', 'warning')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/election_periods/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_election_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    form = ElectionPeriodForm(obj=period)
    if form.validate_on_submit():
        period.name = form.name.data
        period.start_date = form.start_date.data
        period.end_date = form.end_date.data
        db.session.commit()
        flash('El periodo electoral ha sido actualizado.', 'success')
        return redirect(url_for('admin.list_election_periods'))
    return render_template('admin/edit_election_period.html', form=form, period=period)

@bp.route('/election_periods/<int:period_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_election_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()
    flash('El periodo electoral ha sido eliminado.', 'success')
    return redirect(url_for('admin.list_election_periods'))

@bp.route('/election_periods/<int:period_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_active_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    period.is_active = not period.is_active
    db.session.commit()
    flash(f'El estado de "{period.name}" ha sido cambiado a {"Activo" if period.is_active else "Inactivo"}.', 'success')
    return redirect(url_for('admin.list_election_periods'))

@bp.route('/election_periods/<int:period_id>/results')
@login_required
@admin_required
def election_results(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    
    results = db.session.query(
        Vote.candidate_list_id,
        func.count(Vote.id)
    ).filter_by(election_period_id=period_id).group_by(Vote.candidate_list_id).all()
    
    votes_by_list = {list_id: count for list_id, count in results}
    
    chart_labels = []
    chart_data = []
    
    for clist in period.lists:
        chart_labels.append(clist.name)
        chart_data.append(votes_by_list.get(clist.id, 0))
        
    return render_template('admin/results.html', 
                           period=period, 
                           chart_labels=chart_labels, 
                           chart_data=chart_data)

@bp.route('/election_periods/<int:period_id>/lists/add', methods=['POST'])
@login_required
@admin_required
def add_list(period_id):
    form = CandidateListForm()
    if form.validate_on_submit():
        new_list = CandidateList(name=form.name.data, election_period_id=period_id)
        if form.image.data:
            picture_file = save_picture(form.image.data, subfolder='list_images')
            new_list.image = picture_file
        db.session.add(new_list)
        db.session.commit()
        flash('Nueva lista creada con éxito.', 'success')
    else:
        flash('No se pudo crear la lista. Revisa los datos.', 'danger')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/lists/<int:list_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_list(list_id):
    candidate_list = CandidateList.query.get_or_404(list_id)
    form = CandidateListForm(obj=candidate_list)
    if form.validate_on_submit():
        candidate_list.name = form.name.data
        if form.image.data:
            picture_file = save_picture(form.image.data, subfolder='list_images')
            candidate_list.image = picture_file
        db.session.commit()
        flash('La lista ha sido actualizada.', 'success')
        return redirect(url_for('admin.manage_election_period', period_id=candidate_list.election_period_id))
    return render_template('admin/edit_list.html', form=form, candidate_list=candidate_list)

@bp.route('/lists/<int:list_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_list(list_id):
    candidate_list = CandidateList.query.get_or_404(list_id)
    period_id = candidate_list.election_period_id
    db.session.delete(candidate_list)
    db.session.commit()
    flash('La lista ha sido eliminada.', 'success')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/lists/<int:list_id>', methods=['GET'])
@login_required
@admin_required
def manage_list(list_id):
    candidate_list = CandidateList.query.get_or_404(list_id)
    form = AddCandidateForm()
    
    period_voters = candidate_list.election_period.voters
    
    candidates_in_period = Candidate.query.join(CandidateList).filter(CandidateList.election_period_id == candidate_list.election_period_id).all()
    assigned_voter_ids = {c.voter_id for c in candidates_in_period}
    
    form.voter.choices = [
        (v.id, f'{v.name} {v.lastname} ({v.cedula})') for v in period_voters if v.id not in assigned_voter_ids
    ]
    
    period_dignities = candidate_list.election_period.dignities.all()
    form.dignity.choices = [(d.id, d.name) for d in period_dignities]
    
    return render_template('admin/manage_list.html', candidate_list=candidate_list, form=form)

@bp.route('/lists/<int:list_id>/candidates/add', methods=['POST'])
@login_required
@admin_required
def add_candidate(list_id):
    candidate_list = CandidateList.query.get_or_404(list_id)
    form = AddCandidateForm()
    period_voters = candidate_list.election_period.voters
    candidates_in_period = Candidate.query.join(CandidateList).filter(CandidateList.election_period_id == candidate_list.election_period_id).all()
    assigned_voter_ids = {c.voter_id for c in candidates_in_period}
    form.voter.choices = [(v.id, f'{v.name} {v.lastname} ({v.cedula})') for v in period_voters if v.id not in assigned_voter_ids]
    
    period_dignities = candidate_list.election_period.dignities.all()
    form.dignity.choices = [(d.id, d.name) for d in period_dignities]

    if form.validate_on_submit():
        existing_candidate = Candidate.query.filter_by(
            candidate_list_id=list_id, 
            dignity_id=form.dignity.data
        ).first()
        if existing_candidate:
            flash(f'La dignidad seleccionada ya está ocupada por {existing_candidate.name}.', 'danger')
            return redirect(url_for('admin.manage_list', list_id=list_id))

        voter = Voter.query.get(form.voter.data)
        new_candidate = Candidate(
            name=f'{voter.name} {voter.lastname}',
            dignity_id=form.dignity.data, 
            candidate_list_id=list_id,
            voter_id=voter.id
        )
        if form.image.data:
            picture_file = save_picture(form.image.data, subfolder='candidate_pics')
            new_candidate.image = picture_file
        db.session.add(new_candidate)
        db.session.commit()
        flash('Nuevo candidato añadido con éxito.', 'success')
    else:
        # Form errors will be flashed by Flask-WTF
        flash('No se pudo añadir al candidato. Revisa los datos.', 'danger')
    return redirect(url_for('admin.manage_list', list_id=list_id))

@bp.route('/candidates/<int:candidate_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    form = EditCandidateForm(obj=candidate)
    
    period_dignities = candidate.candidate_list.election_period.dignities.all()
    form.dignity.choices = [(d.id, d.name) for d in period_dignities]

    if form.validate_on_submit():
        existing_candidate = Candidate.query.filter_by(
            candidate_list_id=candidate.candidate_list_id, 
            dignity_id=form.dignity.data
        ).first()
        if existing_candidate and existing_candidate.id != candidate.id:
            flash(f'La dignidad seleccionada ya está ocupada por {existing_candidate.name}.', 'danger')
            return redirect(url_for('admin.edit_candidate', candidate_id=candidate_id))

        candidate.dignity_id = form.dignity.data
        if form.image.data:
            picture_file = save_picture(form.image.data, subfolder='candidate_pics')
            candidate.image = picture_file
        db.session.commit()
        flash('El candidato ha sido actualizado.', 'success')
        return redirect(url_for('admin.manage_list', list_id=candidate.candidate_list_id))
    
    if request.method == 'GET':
        form.dignity.data = candidate.dignity_id

    return render_template('admin/edit_candidate.html', form=form, candidate=candidate)


@bp.route('/candidates/<int:candidate_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    list_id = candidate.candidate_list_id
    db.session.delete(candidate)
    db.session.commit()
    flash('El candidato ha sido eliminado.', 'success')
    return redirect(url_for('admin.manage_list', list_id=list_id))

@bp.route('/voters/<int:voter_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_voter(voter_id):
    voter = Voter.query.get_or_404(voter_id)
    from_period_id = request.args.get('from_period', type=int)
    form = VoterForm(obj=voter, original_cedula=voter.cedula)
    if form.validate_on_submit():
        voter.name = form.name.data
        voter.lastname = form.lastname.data
        voter.cedula = form.cedula.data
        db.session.commit()
        flash('Información del votante actualizada.', 'success')
        if from_period_id:
            return redirect(url_for('admin.manage_election_period', period_id=from_period_id))
        else:
            return redirect(url_for('admin.admin_dashboard'))
            
    return render_template('admin/edit_voter.html', form=form, voter=voter, from_period=from_period_id)


@bp.route('/users')
@login_required
@superadmin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    
    if search:
        query = query.filter(User.username.ilike(f'%{search}%'))
        
    if role_filter == 'superadmin':
        query = query.filter(User.is_superadmin == True)
    elif role_filter == 'admin':
        query = query.filter(User.is_admin == True, User.is_superadmin == False)
    elif role_filter == 'student':
        query = query.filter(User.is_admin == False, User.is_superadmin == False)
        
    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/list_users.html', pagination=pagination, search=search, role_filter=role_filter)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@superadmin_required
def add_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {user.username} creado exitosamente.', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/add_user.html', form=form)

@bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@superadmin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('No puedes cambiar tu propio estado de administrador.', 'danger')
    elif user.is_superadmin:
        flash('No se pueden modificar los permisos de otro super administrador.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'{user.username} es ahora {"un administrador" if user.is_admin else "un usuario normal"}.', 'success')
    return redirect(url_for('admin.list_users'))

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_superadmin and user.id != current_user.id:
        flash('No puedes editar a otro super administrador.', 'danger')
        return redirect(url_for('admin.list_users'))
        
    form = EditUserForm(obj=user, original_username=user.username)
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('admin.list_users'))
        
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
    elif user.is_superadmin:
        flash('No puedes eliminar a un super administrador.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'El usuario {user.username} ha sido eliminado del sistema.', 'success')
    return redirect(url_for('admin.list_users'))

@bp.route('/superadmin/login_as/<int:user_id>', methods=['POST'])
@login_required
@superadmin_required
def login_as(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_superadmin and user.id != current_user.id:
        flash('No puedes impersonar a otro super administrador.', 'danger')
        return redirect(url_for('admin.list_users'))
    
    session['impersonator_id'] = current_user.id
    login_user(user)
    flash(f'Sesión iniciada como {user.username}.', 'success')
    
    if user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('main.index'))

@bp.route('/superadmin/revert_impersonation')
@login_required
def revert_impersonation():
    impersonator_id = session.pop('impersonator_id', None)
    if impersonator_id:
        superadmin = User.query.get(impersonator_id)
        if superadmin and superadmin.is_superadmin:
            login_user(superadmin)
            flash('Has regresado a tu rol de Super Admin.', 'success')
            return redirect(url_for('admin.list_users'))
    
    flash('No se pudo restaurar la sesión original.', 'danger')
    return redirect(url_for('main.index'))
