from flask import render_template, flash, redirect, url_for
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from src.main import bp
from src.models import ElectionPeriod, CandidateList, Vote, User


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
