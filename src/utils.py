import os
import secrets
import pandas as pd
from werkzeug.security import generate_password_hash
from sqlalchemy import insert, select
from src import db
from src.models import Voter, ElectionPeriod, User, voter_period_association

def save_picture(form_picture, subfolder='profile_pics'):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join('src/static/uploads', subfolder, picture_fn)

    output_dir = os.path.dirname(picture_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    form_picture.save(picture_path)

    return f"uploads/{subfolder}/{picture_fn}"

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

    # 1. Limpieza inicial: Remover nulos y duplicados dentro del mismo archivo
    df['cedula'] = df['cedula'].astype(str).str.strip()
    df = df[df['cedula'] != 'nan']
    df = df[df['cedula'] != '']
    df = df.drop_duplicates(subset=['cedula'])
    
    excel_cedulas = df['cedula'].tolist()
    if not excel_cedulas:
        return

    # 2. Identificar Votantes Nuevos
    existing_voters = Voter.query.filter(Voter.cedula.in_(excel_cedulas)).all()
    existing_voters_set = {v.cedula for v in existing_voters}

    new_voters_data = []
    for index, row in df.iterrows():
        if row['cedula'] not in existing_voters_set:
            new_voters_data.append({
                'cedula': row['cedula'],
                'name': row['name'],
                'lastname': row['lastname']
            })

    # === BULK INSERT 1: VOTERS ===
    if new_voters_data:
        db.session.execute(insert(Voter), new_voters_data)
        db.session.commit()

    # Re-consultar todos los votantes para obtener sus IDs autogenerados
    all_voters = Voter.query.filter(Voter.cedula.in_(excel_cedulas)).all()
    voter_id_map = {v.cedula: v.id for v in all_voters}

    # 3. Identificar Usuarios (Cuentas) Nuevas
    existing_users = User.query.filter(User.username.in_(excel_cedulas)).all()
    existing_users_set = {u.username for u in existing_users}

    new_users_data = []
    for cedula, v_id in voter_id_map.items():
        if cedula not in existing_users_set:
            # Utilizamos pbkdf2 optimizado a 10k iteraciones para no colapsar la carga masiva
            hashed_pwd = generate_password_hash(cedula, method='pbkdf2:sha256:10000')
            new_users_data.append({
                'username': cedula,
                'password_hash': hashed_pwd,
                'is_admin': False,
                'is_superadmin': False,
                'voter_id': v_id
            })

    # === BULK INSERT 2: USERS ===
    if new_users_data:
        db.session.execute(insert(User), new_users_data)
        db.session.commit()

    # 4. Vincular Votantes con el Periodo Electoral
    # Consultar qué votantes ya están empadronados en este periodo
    stmt = select(voter_period_association.c.voter_id).where(voter_period_association.c.election_period_id == period_id)
    existing_bindings = db.session.execute(stmt).fetchall()
    
    bound_voter_ids = {row[0] for row in existing_bindings}

    new_bindings = []
    for v_id in voter_id_map.values():
        if v_id not in bound_voter_ids:
            new_bindings.append({
                'voter_id': v_id,
                'election_period_id': period_id
            })

    # === BULK INSERT 3: ASOCIACIÓN (PADRÓN) ===
    if new_bindings:
        db.session.execute(insert(voter_period_association), new_bindings)
        db.session.commit()
