from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from src.voting import bp
from src import db
from src.models import ElectionPeriod, CandidateList, Vote, Voter, VoterParticipation

@bp.route('/<int:period_id>/lists', methods=['GET'])
@login_required
def show_lists(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    if not period.is_voting_open:
        flash('Esta elección no está activa actualmente o se encuentra fuera de horario.', 'warning')
        return redirect(url_for('main.index'))

    # Check if the current user (as a voter) is in the election period's voter roll
    if not current_user.voter or current_user.voter not in period.voters:
        flash('No te encuentras en el padrón electoral de este periodo. No puedes participar.', 'danger')
        return redirect(url_for('main.index'))

    # Check if the current user (as a voter) has already voted in this period
    existing_participation = VoterParticipation.query.filter_by(
        voter_id=current_user.voter_id, 
        election_period_id=period.id
    ).first()

    if existing_participation:
        flash('Ya has emitido tu voto en este proceso electoral.', 'info')
        return redirect(url_for('main.index'))

    lists = CandidateList.query.filter_by(election_period_id=period.id).all()
    return render_template('voting/show_lists.html', period=period, lists=lists)

@bp.route('/<int:period_id>/cast_vote/<int:list_id>', methods=['POST'])
@login_required
def cast_vote(period_id, list_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    candidate_list = CandidateList.query.get_or_404(list_id)

    if not period.is_voting_open:
        flash('No se puede votar. La elección no está activa o se encuentra fuera de horario.', 'danger')
        return redirect(url_for('.show_lists', period_id=period_id))

    # Verify the list belongs to the correct election period
    if candidate_list.election_period_id != period.id:
        abort(404) # Or a more user-friendly error

    # Check if the current user (as a voter) is in the election period's voter roll
    if not current_user.voter or current_user.voter not in period.voters:
        flash('Intento de voto rechazado: No te encuentras en el padrón electoral de este periodo.', 'danger')
        return redirect(url_for('main.index'))

    # Double-check if a vote has been cast
    existing_participation = VoterParticipation.query.filter_by(
        voter_id=current_user.voter_id, 
        election_period_id=period.id
    ).first()
    
    if existing_participation:
        flash('Ya has votado en esta elección. No se permiten votos múltiples.', 'warning')
        return redirect(url_for('main.index'))

    try:
        new_participation = VoterParticipation(
            voter_id=current_user.voter_id,
            election_period_id=period.id
        )
        new_vote = Vote(
            election_period_id=period.id,
            candidate_list_id=list_id
        )
        db.session.add(new_participation)
        db.session.add(new_vote)
        db.session.commit()
        flash('¡Tu voto ha sido registrado exitosamente!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al registrar tu voto. Por favor, intenta de nuevo.', 'danger')

    return redirect(url_for('main.index'))

from flask import request, jsonify
@bp.route('/validate_face', methods=['POST'])
@login_required
def validate_face():
    import json
    import numpy as np
    
    data = request.get_json()
    if not data or 'descriptor' not in data:
        return jsonify({'success': False, 'message': 'Descriptor no recibido'}), 400
        
    if not current_user.voter or not current_user.voter.face_descriptor:
        return jsonify({'success': False, 'message': 'No tienes un Face ID registrado'}), 400
        
    try:
        live_data = data['descriptor']
        if isinstance(live_data, dict):
            live_data = list(live_data.values())
        live_descriptor = np.array(live_data, dtype=float)
        
        loaded_desc = json.loads(current_user.voter.face_descriptor)
        if isinstance(loaded_desc, dict):
            loaded_desc = list(loaded_desc.values())
        registered_descriptor = np.array(loaded_desc, dtype=float)
        
        # Calcular distancia Euclidiana
        distance = np.linalg.norm(live_descriptor - registered_descriptor)
        
        # Umbral de tolerancia (típicamente 0.6 para modelos face-api.js)
        # Se subió a 0.62 para ser más permisivo con cámaras de menor resolución o mala luz.
        if distance <= 0.62:
            return jsonify({'success': True, 'match': True, 'distance': float(distance)})
        else:
            return jsonify({'success': True, 'match': False, 'distance': float(distance)})
    except Exception as e:
        print("Error validando rostro:", str(e))
        return jsonify({'success': False, 'message': 'Error procesando biometría'}), 500
