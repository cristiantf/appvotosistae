
import pandas as pd
from src import db
from src.models import Voter, ElectionPeriod, User

def load_voters_from_excel(filepath, period_id):
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath, dtype=str)
        else:
            df = pd.read_excel(filepath, dtype=str)
    except Exception as e:
        raise ValueError(f"Could not read the file: {e}")

    # Normalizar nombres de columnas a minúsculas y sin tildes/espacios
    df.columns = df.columns.str.lower().str.strip().str.replace('é', 'e').str.replace('nombres', 'name').str.replace('apellidos', 'lastname')

    required_columns = ['cedula', 'name', 'lastname']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"El archivo debe contener las columnas: cedula, nombres (o name), apellidos (o lastname). Columnas detectadas: {list(df.columns)}")

    election_period = ElectionPeriod.query.get(period_id)
    if not election_period:
        raise ValueError(f"Election period with id {period_id} not found.")

    df['cedula'] = df['cedula'].astype(str).str.strip()
    existing_voters = Voter.query.filter(Voter.cedula.in_(df['cedula'].tolist())).all()
    existing_voters_dict = {v.cedula: v for v in existing_voters}

    existing_users = User.query.filter(User.username.in_(df['cedula'].tolist())).all()
    existing_users_dict = {u.username: u for u in existing_users}

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

        user = existing_users_dict.get(cedula)
        if not user:
            user = User(username=cedula, voter=voter)
            user.set_password(cedula)
            db.session.add(user)
            existing_users_dict[cedula] = user

    db.session.commit()

