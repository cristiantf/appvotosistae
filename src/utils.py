
import pandas as pd
from src import db
from src.models import Voter, ElectionPeriod

def load_voters_from_excel(filepath, period_id):
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        raise ValueError(f"Could not read the Excel file: {e}")

    required_columns = ['cedula', 'name', 'lastname']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel file must contain the columns: {required_columns}")

    election_period = ElectionPeriod.query.get(period_id)
    if not election_period:
        raise ValueError(f"Election period with id {period_id} not found.")

    for index, row in df.iterrows():
        cedula = str(row['cedula'])
        
        # Find existing voter or create a new one
        voter = Voter.query.filter_by(cedula=cedula).first()
        if not voter:
            voter = Voter(
                cedula=cedula,
                name=row['name'],
                lastname=row['lastname']
            )
            db.session.add(voter)
            # Commit is not strictly necessary here, as the relationship
            # is managed by SQLAlchemy, but can be useful for very large imports.

        # Add the voter to the election period if not already present
        if voter not in election_period.voters:
            election_period.voters.append(voter)

    db.session.commit()
