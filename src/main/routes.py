from flask import render_template, flash, redirect, url_for, request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from src.main import bp
from src.models import ElectionPeriod, CandidateList, Vote, User
from flask_login import login_required, current_user
from src import db
from src.auth.forms import UserProfileForm
from src.utils import save_picture

@bp.route('/')
@bp.route('/index')
def index():
    try:
        all_elections = ElectionPeriod.query.all()
        active_elections = [e for e in all_elections if e.current_status == 'active']
        upcoming_elections = [e for e in all_elections if e.current_status == 'pending']
    except SQLAlchemyError:
        flash('Error de base de datos: no se pudieron cargar las elecciones.', 'danger')
        active_elections = []
        upcoming_elections = []
    return render_template('index.html', title='Home', elections=active_elections, upcoming_elections=upcoming_elections)


@bp.route('/results')
def results():
    try:
        all_elections = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).all()
        finished_elections = [e for e in all_elections if e.current_status in ('finished', 'manual_inactive')]
    except SQLAlchemyError:
        flash('Error de base de datos: no se pudieron cargar los resultados.', 'danger')
        finished_elections = []
    return render_template('main/results.html', elections=finished_elections)


@bp.route('/results/<int:period_id>')
def period_results(period_id):
    try:
        period = ElectionPeriod.query.get_or_404(period_id)
        if period.current_status in ('active', 'pending'):
            flash('Los resultados para esta elección aún no están disponibles.', 'info')
            return redirect(url_for('main.results'))

        results = (
            db.session.query(
                CandidateList.id,
                CandidateList.name,
                CandidateList.image,
                func.count(Vote.id).label('vote_count')
            )
            .outerjoin(Vote, Vote.candidate_list_id == CandidateList.id)
            .filter(CandidateList.election_period_id == period_id)
            .group_by(CandidateList.id)
            .order_by(func.count(Vote.id).desc())
            .all()
        )

        total_votes = Vote.query.filter_by(election_period_id=period_id).count()

    except SQLAlchemyError:
        db.session.rollback()
        flash('Error de base de datos: no se pudieron cargar los resultados del periodo.', 'danger')
        return redirect(url_for('main.results'))

    return render_template('main/period_results.html', period=period, lists_results=results, total_votes=total_votes)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('main.profile'))
            
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
            
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data, subfolder='profile_pics')
            current_user.profile_picture = picture_file
            
        db.session.commit()
        flash('Tu perfil ha sido actualizado con éxito.', 'success')
        return redirect(url_for('main.profile'))
        
    return render_template('main/profile.html', title='Mi Perfil', form=form)

@bp.route('/register_face', methods=['POST'])
@login_required
def register_face():
    import json
    data = request.get_json()
    if not data or 'descriptor' not in data:
        return jsonify({'success': False, 'message': 'Datos biométricos no recibidos'}), 400
        
    descriptor = data['descriptor']
    if isinstance(descriptor, dict):
        descriptor = list(descriptor.values())
        
    # Guardamos como JSON string en la base de datos
    current_user.voter.face_descriptor = json.dumps(descriptor)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Face ID registrado exitosamente'})
