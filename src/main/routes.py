from flask import render_template, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
from src.main import bp
from src.models import ElectionPeriod, CandidateList

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/results')
def results():
    try:
        finished_elections = ElectionPeriod.query.filter_by(is_active=False).order_by(ElectionPeriod.id.desc()).all()
    except SQLAlchemyError as e:
        flash('Database error: could not load election results.', 'danger')
        finished_elections = []
    return render_template('main/results.html', elections=finished_elections)


@bp.route('/results/<int:period_id>')
def period_results(period_id):
    try:
        period = ElectionPeriod.query.get_or_404(period_id)
        
        if period.is_active:
            flash('Results for this election are not yet available.', 'info')
            return redirect(url_for('main.results'))

        lists = CandidateList.query.filter_by(election_period_id=period.id).order_by(CandidateList.vote_count.desc()).all()
        total_votes = sum(list.vote_count for list in lists)

    except SQLAlchemyError as e:
        flash('Database error: could not load period results.', 'danger')
        return redirect(url_for('main.results'))

    return render_template('main/period_results.html', period=period, lists=lists, total_votes=total_votes)
