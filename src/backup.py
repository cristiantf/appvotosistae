import os
import json
import zipfile
import io
import pandas as pd
from datetime import datetime
from sqlalchemy import func
from src import db
from src.models import ElectionPeriod, CandidateList, Candidate, Dignity, Voter, Vote, VoterParticipation, AuditLog
from src.admin.routes import ActaPDF

def get_backup_dir():
    dir_path = os.path.join(os.getcwd(), 'src', 'static', 'backups')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def generate_election_backup(period_id):
    period = ElectionPeriod.query.get(period_id)
    if not period:
        raise ValueError(f"No se encontró el periodo con ID {period_id}")

    # 1. Generar Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Resultados
        results = db.session.query(
            Vote.candidate_list_id, func.count(Vote.id)
        ).filter_by(election_period_id=period_id).group_by(Vote.candidate_list_id).all()
        votes_by_list = {list_id: count for list_id, count in results}
        
        resumen_data = []
        for clist in period.lists:
            resumen_data.append({
                "Lista": clist.name,
                "Votos": votes_by_list.get(clist.id, 0)
            })
        pd.DataFrame(resumen_data).to_excel(writer, index=False, sheet_name="Resultados")
        
        # Candidatos
        candidatos_data = []
        for clist in period.lists:
            for cand in clist.candidates:
                candidatos_data.append({
                    "Lista": clist.name,
                    "Candidato": cand.name,
                    "Dignidad": cand.dignity.name if cand.dignity else "Ninguna",
                    "Cédula Estudiante": cand.voter_info.cedula if cand.voter_info else "N/A"
                })
        pd.DataFrame(candidatos_data).to_excel(writer, index=False, sheet_name="Candidatos")
        
        # Padrón
        padron_data = [{"Cédula": v.cedula, "Nombre": v.name, "Apellido": v.lastname} for v in period.voters]
        pd.DataFrame(padron_data).to_excel(writer, index=False, sheet_name="Padron")
        
        # Participación
        participacion_data = [{"Cédula": p.voter.cedula, "Nombre": p.voter.name, "Fecha y Hora": str(p.timestamp)} for p in period.participations]
        pd.DataFrame(participacion_data).to_excel(writer, index=False, sheet_name="Participacion")

    # 2. Generar PDF (Reutilizamos lógica de ActaPDF)
    pdf = ActaPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 8, "Acta de Respaldo", new_x="LMARGIN", new_y="NEXT", align='C')
    total_padron = len(period.voters)
    total_votes = sum([d["Votos"] for d in resumen_data])
    pdf.cell(0, 8, f"Elección: {period.name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Votos Totales: {total_votes} de {total_padron} empadronados", new_x="LMARGIN", new_y="NEXT")
    pdf_buffer = pdf.output(dest='S')
    
    # 3. Generar JSON
    data_json = {
        "period": {
            "name": period.name,
            "start_date": str(period.start_date) if period.start_date else None,
            "end_date": str(period.end_date) if period.end_date else None,
            "is_active": period.is_active
        },
        "dignities": [{"name": d.name, "old_id": d.id} for d in period.dignities],
        "lists": [{"name": l.name, "image": l.image, "old_id": l.id} for l in period.lists],
        "voters": [{"cedula": v.cedula, "name": v.name, "lastname": v.lastname} for v in period.voters],
        "candidates": [{"name": c.name, "dignity_old_id": c.dignity_id, "list_old_id": c.candidate_list_id, "voter_cedula": c.voter_info.cedula, "image": c.image} for c in period.lists.join(Candidate).with_entities(Candidate).all()],
        "votes": [{"list_old_id": v.candidate_list_id, "timestamp": str(v.timestamp)} for v in period.votes],
        "participations": [{"voter_cedula": p.voter.cedula, "timestamp": str(p.timestamp)} for p in period.participations]
    }
    
    # Wait, the Candidates query needs to be simpler:
    cands_json = []
    for clist in period.lists:
        for cand in clist.candidates:
            cands_json.append({
                "name": cand.name,
                "dignity_old_id": cand.dignity_id,
                "list_old_id": cand.candidate_list_id,
                "voter_cedula": cand.voter_info.cedula if cand.voter_info else None,
                "image": cand.image
            })
    data_json["candidates"] = cands_json

    # 4. Crear ZIP
    filename = f"Respaldo_{period.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    filepath = os.path.join(get_backup_dir(), filename)
    
    with zipfile.ZipFile(filepath, 'w') as zipf:
        zipf.writestr("reporte.xlsx", excel_buffer.getvalue())
        zipf.writestr("acta_oficial.pdf", pdf_buffer)
        zipf.writestr("data.json", json.dumps(data_json, indent=4))
        
    period.backup_generated = True
    db.session.commit()
    
    return filepath

def restore_election_backup(zip_filepath):
    with zipfile.ZipFile(zip_filepath, 'r') as zipf:
        if "data.json" not in zipf.namelist():
            raise ValueError("El archivo ZIP no contiene data.json")
        data = json.loads(zipf.read("data.json"))
        
    p_data = data["period"]
    new_period = ElectionPeriod(
        name=f"[RESTAURADO] {p_data['name']}",
        start_date=datetime.fromisoformat(p_data['start_date']) if p_data['start_date'] else None,
        end_date=datetime.fromisoformat(p_data['end_date']) if p_data['end_date'] else None,
        is_active=False,
        backup_generated=True
    )
    db.session.add(new_period)
    db.session.flush() # Para obtener ID
    
    # Mapeos de IDs antiguos a nuevos
    dignity_map = {}
    for d in data.get("dignities", []):
        new_d = Dignity(name=d["name"], election_period_id=new_period.id)
        db.session.add(new_d)
        db.session.flush()
        dignity_map[d["old_id"]] = new_d.id
        
    list_map = {}
    for l in data.get("lists", []):
        new_l = CandidateList(name=l["name"], image=l.get("image"), election_period_id=new_period.id)
        db.session.add(new_l)
        db.session.flush()
        list_map[l["old_id"]] = new_l.id
        
    # Restaurar votantes
    voter_map = {}
    existing_voters = {v.cedula: v for v in Voter.query.all()}
    for v in data.get("voters", []):
        if v["cedula"] in existing_voters:
            voter = existing_voters[v["cedula"]]
        else:
            voter = Voter(cedula=v["cedula"], name=v["name"], lastname=v["lastname"])
            db.session.add(voter)
            db.session.flush()
            existing_voters[v["cedula"]] = voter
        
        new_period.voters.append(voter)
        voter_map[v["cedula"]] = voter.id
        
    # Candidatos
    for c in data.get("candidates", []):
        new_c = Candidate(
            name=c["name"],
            image=c.get("image"),
            candidate_list_id=list_map.get(c["list_old_id"]),
            dignity_id=dignity_map.get(c["dignity_old_id"]),
            voter_id=voter_map.get(c["voter_cedula"])
        )
        db.session.add(new_c)
        
    # Votos
    for v in data.get("votes", []):
        new_v = Vote(
            election_period_id=new_period.id,
            candidate_list_id=list_map.get(v["list_old_id"]),
            timestamp=datetime.fromisoformat(v["timestamp"])
        )
        db.session.add(new_v)
        
    # Participaciones
    for p in data.get("participations", []):
        new_p = VoterParticipation(
            election_period_id=new_period.id,
            voter_id=voter_map.get(p["voter_cedula"]),
            timestamp=datetime.fromisoformat(p["timestamp"])
        )
        db.session.add(new_p)
        
    # Auditar la restauración
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        audit = AuditLog(user_id=current_user.id, action=f"Periodo Restaurado desde Respaldo: {new_period.name}")
        db.session.add(audit)
        
    db.session.commit()
    return new_period.id
