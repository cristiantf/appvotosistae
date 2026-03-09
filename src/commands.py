
# src/commands.py
import click
from flask.cli import with_appcontext
from src import db
from src.models import Candidate, Voter

@click.command(name='clean-orphans')
@with_appcontext
def clean_orphans():
    """Finds and deletes orphaned candidates from the database."""
    candidates_to_delete = []
    all_candidates = Candidate.query.all()
    
    click.echo(f"Found {len(all_candidates)} candidates to check.")
    
    for candidate in all_candidates:
        if candidate.voter_id is None:
            click.echo(f"Candidate with ID={candidate.id} has no voter_id. Marked for deletion.")
            candidates_to_delete.append(candidate)
            continue

        # Use a direct query to check for the voter's existence to avoid loading the full object
        voter_exists = db.session.query(Voter.id).filter_by(id=candidate.voter_id).first() is not None
        if not voter_exists:
            click.echo(f"Orphaned candidate found: ID={candidate.id}, Name='{candidate.name}', Invalid voter_id={candidate.voter_id}. Marked for deletion.")
            candidates_to_delete.append(candidate)

    if not candidates_to_delete:
        click.echo("No orphaned candidates found. The database is clean.")
    else:
        click.echo(f"Deleting {len(candidates_to_delete)} orphaned or invalid candidates...")
        for candidate in candidates_to_delete:
            db.session.delete(candidate)
        db.session.commit()
        click.echo("Deletion complete.")
