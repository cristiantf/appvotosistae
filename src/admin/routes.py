
import os
import secrets
import io
import pandas as pd
from datetime import datetime
from fpdf import FPDF
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
from src.utils import load_voters_from_excel, save_picture
from werkzeug.utils import secure_filename
from src.decorators import admin_required, superadmin_required
from flask_login import login_user

def log_admin_action(action, details=None):
    if current_user.is_authenticated:
        log = AuditLog(user_id=current_user.id, action=action, details=details)
        db.session.add(log)

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
            log_admin_action(f"Padron subido masivamente para el periodo ID {period_id} (Archivo: {filename})")
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
        
        log_admin_action(f"Creado periodo electoral: {new_period.name}")
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
        log_admin_action(f"Añadida dignidad '{form.name.data}' al periodo ID {period_id}")
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
    log_admin_action(f"Eliminada dignidad '{dignity.name}' del periodo ID {period_id}")
    db.session.commit()
    flash('Dignidad eliminada.', 'success')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/dignities/<int:dignity_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_dignity(dignity_id):
    dignity = Dignity.query.get_or_404(dignity_id)
    period_id = dignity.election_period_id
    new_name = request.form.get('name')
    
    if new_name and new_name.strip():
        dignity.name = new_name.strip()
        log_admin_action(f"Dignidad ID {dignity_id} renombrada a '{new_name.strip()}'")
        db.session.commit()
        flash('Dignidad actualizada correctamente.', 'success')
    else:
        flash('El nombre del cargo no puede estar vacío.', 'danger')
        
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
        log_admin_action(f"Votante {voter.cedula} removido del periodo ID {period_id}")
        db.session.commit()
        flash(f'El votante {voter.name} {voter.lastname} ha sido removido del periodo.', 'success')
    else:
        flash('El votante no se encuentra en este periodo electoral.', 'warning')
    return redirect(url_for('admin.manage_election_period', period_id=period_id))

@bp.route('/election_periods/<int:period_id>/add_single_voter', methods=['POST'])
@login_required
@admin_required
def add_single_voter_to_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    search_term = request.form.get('cedula', '').strip()
    
    if not search_term:
        flash('Debe ingresar un término de búsqueda.', 'danger')
        return redirect(url_for('admin.manage_election_period', period_id=period_id))
        
    # Buscar en tabla Voter (por cédula exacta, nombre o apellido)
    voters_found = Voter.query.filter(
        db.or_(
            Voter.cedula == search_term,
            Voter.name.ilike(f'%{search_term}%'),
            Voter.lastname.ilike(f'%{search_term}%'),
            db.func.concat(Voter.name, ' ', Voter.lastname).ilike(f'%{search_term}%')
        )
    ).all()
    
    # Si no se encuentra Voter, buscar en tabla User
    if not voters_found:
        users_found = User.query.filter(
            db.or_(
                User.username == search_term,
                User.name.ilike(f'%{search_term}%'),
                User.lastname.ilike(f'%{search_term}%'),
                db.func.concat(User.name, ' ', User.lastname).ilike(f'%{search_term}%')
            )
        ).all()
        
        if not users_found:
            flash(f'No se encontró ningún estudiante o usuario registrado con la búsqueda "{search_term}".', 'danger')
            return redirect(url_for('admin.manage_election_period', period_id=period_id))
            
        if len(users_found) > 1:
            flash(f'Se encontraron varios usuarios con el término "{search_term}". Por favor ingresa el nombre de usuario o cédula exacta.', 'warning')
            return redirect(url_for('admin.manage_election_period', period_id=period_id))
            
        user = users_found[0]
        # Creamos el perfil de Voter si solo existía como User
        voter = Voter(
            cedula=user.username,
            name=user.name or user.username,
            lastname=user.lastname or ''
        )
        db.session.add(voter)
        user.voter = voter
        db.session.flush()
    else:
        if len(voters_found) > 1:
            flash(f'Se encontraron varios estudiantes con el término "{search_term}". Por favor ingresa la cédula exacta.', 'warning')
            return redirect(url_for('admin.manage_election_period', period_id=period_id))
        voter = voters_found[0]
        
    if voter in period.voters:
        flash(f'El estudiante {voter.name} {voter.lastname} ya pertenece al padrón de este periodo.', 'info')
    else:
        period.voters.append(voter)
        log_admin_action(f"Agregado manualmente al padrón del periodo {period.name}: Cédula/Usuario {voter.cedula}")
        db.session.commit()
        flash(f'Estudiante {voter.name} {voter.lastname} agregado exitosamente al padrón.', 'success')
        
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
        log_admin_action(f"Editado periodo electoral '{period.name}'")
        db.session.commit()
        flash('El periodo electoral ha sido actualizado.', 'success')
        return redirect(url_for('admin.list_election_periods'))
    return render_template('admin/edit_election_period.html', form=form, period=period)

@bp.route('/election_periods/<int:period_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_election_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    
    from src.backup import generate_election_backup
    try:
        generate_election_backup(period.id)
        log_admin_action(f"Respaldo automático de seguridad generado por eliminación de '{period.name}'")
    except Exception as e:
        flash(f'Error Crítico: No se pudo generar el respaldo de seguridad. Eliminación abortada para proteger los datos. ({e})', 'danger')
        return redirect(url_for('admin.list_election_periods'))
        
    db.session.delete(period)
    log_admin_action(f"Eliminado periodo electoral '{period.name}' (ID {period_id})")
    db.session.commit()
    flash('El periodo electoral ha sido eliminado. Se ha guardado una copia en el Gestor de Respaldos por seguridad.', 'success')
    return redirect(url_for('admin.list_election_periods'))

@bp.route('/election_periods/<int:period_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_active_period(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    period.is_active = not period.is_active
    log_admin_action(f"Estado del periodo '{period.name}' cambiado a {'Activo' if period.is_active else 'Inactivo'}")
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

class ActaPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Acta Oficial de Escrutinio', border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, 'Sistema de Votación Estudiantil - IPA26', border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

@bp.route('/election_periods/<int:period_id>/acta_pdf')
@login_required
@admin_required
def download_acta_pdf(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    
    # Calcular resultados
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
        
    total_votes = sum(chart_data)
    total_padron = len(period.voters)
    participacion = (total_votes / total_padron * 100) if total_padron > 0 else 0
    
    # Crear PDF
    pdf = ActaPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # Información General
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, "Información de la Elección", new_x="LMARGIN", new_y="NEXT", fill=True)
    
    pdf.set_font("helvetica", '', 11)
    pdf.cell(50, 8, "Periodo Electoral:")
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 8, period.name, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", '', 11)
    pdf.cell(50, 8, "Fecha de Inicio:")
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 8, period.start_date.strftime('%Y-%m-%d %H:%M') if period.start_date else 'No definida', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", '', 11)
    pdf.cell(50, 8, "Fecha de Cierre:")
    pdf.set_font("helvetica", 'B', 11)
    pdf.cell(0, 8, period.end_date.strftime('%Y-%m-%d %H:%M') if period.end_date else 'No definida', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Participación
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 8, "Resumen de Participación", new_x="LMARGIN", new_y="NEXT", fill=True)
    
    pdf.set_font("helvetica", '', 11)
    pdf.cell(80, 8, "Estudiantes Empadronados (Habilitados):", border=1)
    pdf.cell(40, 8, str(total_padron), border=1, align='R', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(80, 8, "Total de Votos Emitidos:", border=1)
    pdf.cell(40, 8, str(total_votes), border=1, align='R', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(80, 8, "Porcentaje de Participación:", border=1)
    pdf.cell(40, 8, f"{participacion:.2f}%", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # Desglose Oficial
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 8, "Desglose Oficial de Votación", new_x="LMARGIN", new_y="NEXT", fill=True)
    
    pdf.set_font("helvetica", 'B', 11)
    pdf.set_fill_color(220, 230, 255)
    pdf.cell(120, 10, "Lista / Opción", border=1, fill=True)
    pdf.cell(40, 10, "Votos Registrados", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", '', 11)
    for idx, list_name in enumerate(chart_labels):
        votos = chart_data[idx]
        pdf.cell(120, 10, list_name, border=1)
        pdf.cell(40, 10, str(votos), border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(30)
    
    # Firmas
    pdf.set_font("helvetica", '', 10)
    pdf.cell(80, 8, "___________________________________", align='C')
    pdf.cell(30, 8, "", align='C') # Espacio
    pdf.cell(80, 8, "___________________________________", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(80, 5, "Presidente del Tribunal Electoral", align='C')
    pdf.cell(30, 5, "", align='C')
    pdf.cell(80, 5, "Secretario(a)", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    pdf.set_font("helvetica", 'I', 8)
    pdf.cell(0, 5, f"Documento generado automáticamente el {datetime.now().strftime('%Y-%m-%d a las %H:%M:%S')}", align='C')
    
    pdf_bytes = pdf.output()
    
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=f"Acta_Escrutinio_{period.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

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
        log_admin_action(f"Añadida lista '{new_list.name}' al periodo ID {period_id}")
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
        log_admin_action(f"Editada lista '{candidate_list.name}' (ID {list_id})")
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
    log_admin_action(f"Eliminada lista '{candidate_list.name}' (ID {list_id})")
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
        log_admin_action(f"Añadido candidato '{new_candidate.name}' a la lista ID {list_id}")
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
        log_admin_action(f"Editado candidato '{candidate.name}' (ID {candidate_id})")
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
    log_admin_action(f"Eliminado candidato '{candidate.name}' (ID {candidate_id})")
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
        log_admin_action(f"Editada información del votante '{voter.cedula}'")
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
    
    query = User.query.outerjoin(Voter, User.voter_id == Voter.id)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(db.or_(
            User.username.ilike(search_term),
            Voter.name.ilike(search_term),
            Voter.lastname.ilike(search_term)
        ))
        
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
        user = User(
            username=form.username.data, 
            name=form.name.data,
            lastname=form.lastname.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        log_admin_action(f"Creado usuario '{user.username}'")
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
        log_admin_action(f"Permisos de administrador {'otorgados' if user.is_admin else 'revocados'} al usuario '{user.username}'")
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
        log_admin_action(f"Editado usuario '{user.username}'")
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
        log_admin_action(f"Eliminado usuario '{user.username}' (ID {user_id})")
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

@bp.route('/logs')
@login_required
@superadmin_required
def view_audit_logs():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = AuditLog.query.join(User)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(db.or_(
            AuditLog.action.ilike(search_term),
            User.username.ilike(search_term)
        ))
        
    pagination = query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/audit_logs.html', pagination=pagination, search=search)

@bp.route('/election_periods/<int:period_id>/backup')
@login_required
@superadmin_required
def generate_manual_backup(period_id):
    from src.backup import generate_election_backup
    try:
        filepath = generate_election_backup(period_id)
        log_admin_action(f"Generado respaldo manual para periodo ID {period_id}")
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error al generar respaldo: {e}', 'danger')
        return redirect(url_for('admin.list_election_periods'))

@bp.route('/election_periods/restore', methods=['POST'])
@login_required
@superadmin_required
def restore_backup():
    if 'backup_file' not in request.files:
        flash('No se subió ningún archivo.', 'danger')
        return redirect(url_for('admin.list_election_periods'))
        
    file = request.files['backup_file']
    if file.filename == '':
        flash('Archivo no seleccionado.', 'danger')
        return redirect(url_for('admin.list_election_periods'))
        
    if file and file.filename.endswith('.zip'):
        from werkzeug.utils import secure_filename
        from src.backup import restore_election_backup
        
        filename = secure_filename(file.filename)
        filepath = os.path.join('src/static/uploads', filename)
        file.save(filepath)
        
        try:
            new_period_id = restore_election_backup(filepath)
            flash('Respaldo restaurado con éxito. Se ha creado una copia exacta del periodo.', 'success')
            return redirect(url_for('admin.manage_election_period', period_id=new_period_id))
        except Exception as e:
            flash(f'Error al restaurar el respaldo: {e}', 'danger')
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        flash('Formato no válido. Debe ser un archivo .zip', 'danger')
        
    return redirect(url_for('admin.list_election_periods'))

@bp.route('/backups')
@login_required
@superadmin_required
def list_backups():
    from src.backup import get_backup_dir
    import math
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    backup_dir = get_backup_dir()
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                size_bytes = os.path.getsize(filepath)
                size_mb = size_bytes / (1024 * 1024)
                creation_time = os.path.getctime(filepath)
                
                backups.append({
                    'filename': filename,
                    'size_mb': round(size_mb, 2),
                    'date': datetime.fromtimestamp(creation_time)
                })
                
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    total = len(backups)
    total_pages = math.ceil(total / per_page)
    
    # Prevenir páginas fuera de rango
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
        
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_backups = backups[start_idx:end_idx]
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1,
        'next_num': page + 1
    }
    
    return render_template('admin/manage_backups.html', backups=paginated_backups, pagination=pagination)

@bp.route('/backups/download/<filename>')
@login_required
@superadmin_required
def download_backup(filename):
    from src.backup import get_backup_dir
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(filename)
    filepath = os.path.join(get_backup_dir(), safe_filename)
    
    if os.path.exists(filepath):
        log_admin_action(f"Descargado archivo de respaldo: {safe_filename}")
        return send_file(filepath, as_attachment=True)
    else:
        flash('El archivo no existe.', 'danger')
        return redirect(url_for('admin.list_backups'))

@bp.route('/backups/delete/<filename>', methods=['POST'])
@login_required
@superadmin_required
def delete_backup(filename):
    from src.backup import get_backup_dir
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(filename)
    filepath = os.path.join(get_backup_dir(), safe_filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        log_admin_action(f"Eliminado permanentemente el respaldo: {safe_filename}")
        flash('Respaldo eliminado permanentemente del servidor.', 'success')
    else:
        flash('El archivo no existe.', 'danger')
        
    return redirect(url_for('admin.list_backups'))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    from src.models import SystemSettings
    from src.admin.forms import SystemSettingsForm
    
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
        
    form = SystemSettingsForm(obj=settings)
    
    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.commit()
        log_admin_action('Se actualizó la configuración global del sistema de registro.')
        flash('Configuración del sistema actualizada correctamente.', 'success')
        return redirect(url_for('admin.system_settings'))
        
    return render_template('admin/settings.html', form=form, settings=settings)
