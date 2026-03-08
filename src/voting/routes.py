from flask import render_template, redirect, url_for, flash, session
from . import voting_bp
from ..models import User, Candidate
from .. import db

@voting_bp.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if user.has_voted:
        flash('You have already voted.', 'warning')
        return redirect(url_for('auth.logout'))

    candidates = Candidate.query.all()
    return render_template('voting.html', candidates=candidates)
