
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

    df['cedula'] = df['cedula'].astype(str).str.strip()
    existing_voters = Voter.query.filter(Voter.cedula.in_(df['cedula'].tolist())).all()
    existing_voters_dict = {v.cedula: v for v in existing_voters}

    for index, row in df.iterrows():
        cedula = row['cedula']
        voter = existing_voters_dict.get(cedula)
        
        if not voter:
            voter = Voter(
                cedula=cedula,
                name=row['name'],
                lastname=row['lastname']
            )
            db.session.add(voter)
            existing_voters_dict[cedula] = voter

        if voter not in election_period.voters:
            election_period.voters.append(voter)

    db.session.commit()

