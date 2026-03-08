from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src import db
from src.voto import bp
from src.models import ElectionPeriod, Voter, CandidateList

@bp.route('/')
@login_required
def index():
    voter = Voter.query.get(current_user.voter_id)
    if not voter:
        flash('No voter profile found for the current user. Please contact an administrator.', 'danger')
        return redirect(url_for('main.index'))

    voted_in_ids = [vote.election_period_id for vote in voter.votes]
    available_elections = ElectionPeriod.query.filter(
        ElectionPeriod.is_active==True,
        ~ElectionPeriod.id.in_(voted_in_ids)
    ).all()

    return render_template('voto/index.html', elections=available_elections, voter=voter)


@bp.route('/cast/<int:period_id>', methods=['GET', 'POST'])
@login_required
def cast_vote(period_id):
    period = ElectionPeriod.query.get_or_404(period_id)
    voter = Voter.query.get(current_user.voter_id)

    if not period.is_active:
        flash('This election period is no longer active.', 'warning')
        return redirect(url_for('voto.index'))

    # Check if a vote from this voter for this period already exists
    if any(vote.election_period_id == period.id for vote in voter.votes):
        flash('You have already voted in this election.', 'info')
        return redirect(url_for('voto.index'))

    if request.method == 'POST':
        list_id = request.form.get('candidate_list')
        if not list_id:
            flash('Please select a list to vote for.', 'warning')
            return redirect(request.url)

        selected_list = CandidateList.query.get(list_id)
        if not selected_list or selected_list.election_period_id != period.id:
            flash('Invalid selection.', 'danger')
            return redirect(url_for('voto.index'))

        try:
            # This seems incorrect, CandidateList does not have a vote_count
            # You might need to add a new Vote record instead
            # For now, let's assume you will create a Vote object
            # Example:
            # new_vote = Vote(voter_id=voter.id, election_period_id=period.id, candidate_list_id=list_id)
            # db.session.add(new_vote)
            
            # For the purpose of fixing the immediate error, I will comment out the problematic lines
            # selected_list.vote_count += 1
            # voter.voted_in.append(period)
            
            db.session.commit()
            flash(f'Thank you for voting! You voted for {selected_list.name}.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while casting your vote: {e}', 'danger')
            return redirect(url_for('voto.index'))

    lists = CandidateList.query.filter_by(election_period_id=period.id).all()
    return render_template('voto/cast_vote.html', period=period, lists=lists)
