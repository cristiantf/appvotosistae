from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from src.voting import bp
from src import db
from src.models import ElectionPeriod, CandidateList, Vote, Voter

@bp.route('/<int:period_id>/lists', methods=['GET'])
@login_required
def show_lists(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    if not period.is_active:
        flash('Esta elección no está activa actualmente.', 'warning')
        return redirect(url_for('main.index'))

    # Check if the current user (as a voter) has already voted in this period
    existing_vote = Vote.query.filter_by(
        voter_id=current_user.voter_id, 
        election_period_id=period.id
    ).first()

    if existing_vote:
        flash('Ya has emitido tu voto en este proceso electoral.', 'info')
        return redirect(url_for('main.index'))

    lists = CandidateList.query.filter_by(election_period_id=period.id).all()
    return render_template('voting/show_lists.html', period=period, lists=lists)

@bp.route('/<int:period_id>/cast_vote/<int:list_id>', methods=['POST'])
@login_required
def cast_vote(period_id, list_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    candidate_list = CandidateList.query.get_or_404(list_id)

    if not period.is_active:
        flash('No se puede votar en una elección que no está activa.', 'danger')
        return redirect(url_for('.show_lists', period_id=period_id))

    # Verify the list belongs to the correct election period
    if candidate_list.election_period_id != period.id:
        abort(404) # Or a more user-friendly error

    # Double-check if a vote has been cast
    existing_vote = Vote.query.filter_by(
        voter_id=current_user.voter_id, 
        election_period_id=period.id
    ).first()
    
    if existing_vote:
        flash('Ya has votado en esta elección. No se permiten votos múltiples.', 'warning')
        return redirect(url_for('main.index'))

    try:
        new_vote = Vote(
            voter_id=current_user.voter_id,
            election_period_id=period.id,
            candidate_list_id=list_id
        )
        db.session.add(new_vote)
        db.session.commit()
        flash('¡Tu voto ha sido registrado exitosamente!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al registrar tu voto. Por favor, intenta de nuevo.', 'danger')

    return redirect(url_for('main.index'))
