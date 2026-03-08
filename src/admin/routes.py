
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from src import db
from src.admin import bp
from src.admin.forms import (
    FileUploadForm, ElectionPeriodForm, CandidateListForm, CandidateForm, VoterForm
)
from src.models import User, Voter, ElectionPeriod, CandidateList, Candidate
from src.decorators import admin_required
import pandas as pd
import os

@bp.route('/')
@login_required
@admin_required
def index():
    try:
        voter_count = Voter.query.count()
        period_count = ElectionPeriod.query.count()
        list_count = CandidateList.query.count()
        users = User.query.all()
    except SQLAlchemyError as e:
        flash('Database error: could not load dashboard data.', 'danger')
        voter_count, period_count, list_count = 0, 0, 0
        users = []
        
    return render_template('admin/index.html', 
                           title='Admin Dashboard', 
                           users=users,
                           voter_count=voter_count,
                           period_count=period_count,
                           list_count=list_count)

@bp.route('/elections', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_elections():
    period_form = ElectionPeriodForm()
    if period_form.validate_on_submit():
        try:
            new_period = ElectionPeriod(name=period_form.name.data)
            db.session.add(new_period)
            db.session.commit()
            flash('New election period has been created.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating election period: {e}', 'danger')
        return redirect(url_for('admin.manage_elections'))

    periods = ElectionPeriod.query.all()
    return render_template('admin/manage_elections.html', title='Manage Elections', 
                           periods=periods, period_form=period_form)

@bp.route('/elections/edit/<int:period_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_election_period(period_id):
    period = db.session.get(ElectionPeriod, period_id)
    if not period:
        flash('Election period not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))

    form = ElectionPeriodForm(obj=period)
    if form.validate_on_submit():
        try:
            period.name = form.name.data
            db.session.commit()
            flash('The election period has been updated.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating election period: {e}', 'danger')
        return redirect(url_for('admin.manage_elections'))

    return render_template('admin/edit_election_period.html', title='Edit Election Period', form=form, period=period)

@bp.route('/elections/delete/<int:period_id>', methods=['POST'])
@login_required
@admin_required
def delete_election_period(period_id):
    period = db.session.get(ElectionPeriod, period_id)
    if not period:
        flash('Election period not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))

    try:
        period.voters = []
        lists = CandidateList.query.filter_by(election_period_id=period.id).all()
        for lst in lists:
            Candidate.query.filter_by(candidate_list_id=lst.id).delete()
            db.session.delete(lst)
        db.session.delete(period)
        db.session.commit()
        flash(f'Election period "{period.name}" and all its related data have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting election period: {e}', 'danger')
    return redirect(url_for('admin.manage_elections'))

@bp.route('/elections/toggle_status/<int:period_id>', methods=['POST'])
@login_required
@admin_required
def toggle_election_status(period_id):
    period = db.session.get(ElectionPeriod, period_id)
    if not period:
        flash('Election period not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))
    try:
        period.is_active = not period.is_active
        db.session.commit()
        status = "activated" if period.is_active else "deactivated"
        flash(f'Election period has been {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling election status: {e}', 'danger')
    return redirect(url_for('admin.manage_elections'))

@bp.route('/elections/<int:period_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_period_details(period_id):
    period = db.session.get(ElectionPeriod, period_id)
    if not period:
        flash('Election period not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))

    list_form = CandidateListForm()
    upload_form = FileUploadForm()
    search_query = request.args.get('search', '')

    if upload_form.validate_on_submit() and 'file' in request.files:
        file = upload_form.file.data
        try:
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath, dtype=str) if filepath.endswith('.csv') else pd.read_excel(filepath, dtype=str)
            df.columns = [col.strip().upper() for col in df.columns]

            for index, row in df.iterrows():
                cedula, name, lastname = row['CÉDULA'], row['NOMBRES'], row['APELLIDOS']
                voter = Voter.query.filter_by(cedula=cedula).first()
                if not voter:
                    voter = Voter(cedula=cedula, name=name, lastname=lastname)
                    db.session.add(voter)
                    db.session.flush()
                else:
                    voter.name, voter.lastname = name, lastname
                if voter not in period.voters:
                    period.voters.append(voter)
                if not User.query.filter_by(voter_id=voter.id).first():
                    user = User(username=cedula, voter_id=voter.id)
                    user.set_password(cedula)
                    db.session.add(user)

            db.session.commit()
            flash('Voters loaded successfully.', 'success')
            os.remove(filepath)
        except Exception as e:
            db.session.rollback()
            flash(f'Error loading voters: {e}', 'danger')
        return redirect(url_for('admin.manage_period_details', period_id=period.id))
    
    if list_form.validate_on_submit():
        try:
            new_list = CandidateList(name=list_form.name.data, election_period_id=period.id)
            db.session.add(new_list)
            db.session.commit()
            flash('New candidate list created.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating list: {e}', 'danger')
        return redirect(url_for('admin.manage_period_details', period_id=period.id))

    voters_query = Voter.query.with_parent(period)
    if search_query:
        search_term = f'%{search_query}%'
        voters_query = voters_query.filter(or_(Voter.cedula.like(search_term), Voter.name.like(search_term), Voter.lastname.like(search_term)))
    
    voters = voters_query.all()
    lists = CandidateList.query.filter_by(election_period_id=period.id).all()
    
    return render_template('admin/manage_period_details.html', title=f'Manage {period.name}', period=period, lists=lists, list_form=list_form, upload_form=upload_form, voters=voters, search_query=search_query)

@bp.route('/voters/edit/<int:voter_id>/<int:period_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_voter(voter_id, period_id):
    voter = db.session.get(Voter, voter_id)
    if not voter:
        flash('Voter not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))

    form = VoterForm(original_cedula=voter.cedula, obj=voter)
    if form.validate_on_submit():
        try:
            voter.name = form.name.data
            voter.lastname = form.lastname.data
            voter.cedula = form.cedula.data
            db.session.commit()
            flash('Voter has been updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating voter: {e}', 'danger')
        return redirect(url_for('admin.manage_period_details', period_id=period_id))

    return render_template('admin/edit_voter.html', title='Edit Voter', form=form, voter=voter, period_id=period_id)

@bp.route('/elections/<int:period_id>/delete_voter/<int:voter_id>', methods=['POST'])
@login_required
@admin_required
def delete_voter_from_period(period_id, voter_id):
    period = db.session.get(ElectionPeriod, period_id)
    voter = db.session.get(Voter, voter_id)
    if not period or not voter:
        flash('Period or voter not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))
    try:
        if voter in period.voters:
            period.voters.remove(voter)
            db.session.commit()
            flash(f'Voter {voter.name} {voter.lastname} has been removed from the period.', 'success')
        else:
            flash('Voter is not associated with this period.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing voter: {e}', 'danger')
    return redirect(url_for('admin.manage_period_details', period_id=period_id))

@bp.route('/lists/edit/<int:list_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate_list(list_id):
    candidate_list = db.session.get(CandidateList, list_id)
    if not candidate_list:
        flash('Candidate list not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))
    form = CandidateListForm(obj=candidate_list)
    if form.validate_on_submit():
        try:
            candidate_list.name = form.name.data
            db.session.commit()
            flash('The candidate list has been updated.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating candidate list: {e}', 'danger')
        return redirect(url_for('admin.manage_period_details', period_id=candidate_list.election_period_id))
    return render_template('admin/edit_candidate_list.html', title='Edit Candidate List', form=form, candidate_list=candidate_list)

@bp.route('/lists/delete/<int:list_id>', methods=['POST'])
@login_required
@admin_required
def delete_candidate_list(list_id):
    candidate_list = db.session.get(CandidateList, list_id)
    if not candidate_list:
        flash('Candidate list not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))
    period_id = candidate_list.election_period_id
    try:
        Candidate.query.filter_by(candidate_list_id=list_id).delete()
        db.session.delete(candidate_list)
        db.session.commit()
        flash(f'Candidate list "{candidate_list.name}" and all its candidates have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting candidate list: {e}', 'danger')
    return redirect(url_for('admin.manage_period_details', period_id=period_id))

@bp.route('/voters/search/<int:period_id>')
@login_required
@admin_required
def search_voters(period_id):
    search_term = request.args.get('q', '')
    period = db.session.get(ElectionPeriod, period_id)
    if not period or not search_term:
        return jsonify([])
    
    search_query = f'%{search_term}%'
    voters = Voter.query.with_parent(period).filter(
        or_(
            Voter.cedula.like(search_query),
            Voter.name.like(search_query),
            Voter.lastname.like(search_query)
        )
    ).all()
    
    results = [{'id': v.id, 'text': f'{v.name} {v.lastname} ({v.cedula})'} for v in voters]
    return jsonify(results)

@bp.route('/lists/<int:list_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_list_details(list_id):
    candidate_list = db.session.get(CandidateList, list_id)
    if not candidate_list:
        flash('Candidate list not found.', 'danger')
        return redirect(url_for('admin.manage_elections'))

    form = CandidateForm()
    if request.method == 'POST':
        voter_id = request.form.get('voter')
        if voter_id:
            voter = db.session.get(Voter, voter_id)
            if voter:
                form.voter.choices = [(voter.id, f'{voter.name} {voter.lastname}')]

    if form.validate_on_submit():
        try:
            voter = db.session.get(Voter, form.voter.data)
            existing_candidate = Candidate.query.filter_by(voter_id=voter.id, candidate_list_id=list_id).first()
            if existing_candidate:
                flash('This voter is already a candidate in this list.', 'warning')
            elif voter:
                new_candidate = Candidate(
                    name=f'{voter.name} {voter.lastname}',
                    dignity=form.dignity.data,
                    candidate_list_id=candidate_list.id,
                    voter_id=voter.id
                )
                db.session.add(new_candidate)
                db.session.commit()
                flash('New candidate has been added.', 'success')
            else:
                flash('Selected voter not found.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding candidate: {e}', 'danger')
        return redirect(url_for('admin.manage_list_details', list_id=list_id))

    candidates = Candidate.query.filter_by(candidate_list_id=list_id).all()
    period = db.session.get(ElectionPeriod, candidate_list.election_period_id)
    return render_template('admin/manage_list_details.html', title=f'Manage {candidate_list.name}', 
                           candidate_list=candidate_list, candidates=candidates, form=form, period=period)
