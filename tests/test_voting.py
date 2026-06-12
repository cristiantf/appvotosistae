import pytest
from flask import url_for
from datetime import datetime, timedelta
from src.models import User, Voter, ElectionPeriod, CandidateList, Vote, VoterParticipation, voter_period_association
from src import db

@pytest.fixture(scope='function')
def setup_election(app):
    """Fixture que crea un proceso electoral con votantes, listas y estado activo."""
    with app.app_context():
        # 1. Crear un Votante y un Usuario
        voter = Voter(cedula='0999999999', name='Test', lastname='Voter')
        db.session.add(voter)
        db.session.commit()
        
        user = User(username='0999999999', is_admin=False, voter_id=voter.id)
        user.set_password('testpassword')
        db.session.add(user)
        
        # 2. Crear un periodo electoral Activo
        now = datetime.now()
        period = ElectionPeriod(
            name='Elecciones 2026', 
            is_active=True, 
            start_date=now - timedelta(days=1), 
            end_date=now + timedelta(days=1)
        )
        db.session.add(period)
        db.session.commit()
        
        # 3. Empadronar al votante
        stmt = voter_period_association.insert().values(voter_id=voter.id, election_period_id=period.id)
        db.session.execute(stmt)
        
        # 4. Crear Listas
        lista_a = CandidateList(name='Lista A', election_period_id=period.id)
        lista_blanco = CandidateList(name='Voto en Blanco', election_period_id=period.id)
        db.session.add(lista_a)
        db.session.add(lista_blanco)
        db.session.commit()
        
        yield {
            'voter': voter,
            'user': user,
            'period': period,
            'lista_a': lista_a,
            'lista_blanco': lista_blanco
        }
        
        # Teardown
        db.session.delete(lista_a)
        db.session.delete(lista_blanco)
        db.session.delete(user)
        db.session.delete(voter)
        db.session.delete(period)
        Vote.query.delete()
        VoterParticipation.query.delete()
        db.session.commit()

def test_cast_vote_success_and_anonymous(client, app, setup_election):
    """Prueba el proceso completo de votación y que el voto sea anónimo."""
    period_id = setup_election['period'].id
    lista_id = setup_election['lista_a'].id
    voter_id = setup_election['voter'].id
    
    with client:
        # Iniciar sesión
        client.post(url_for('auth.login'), data={
            'username': '0999999999',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        # Votar por la Lista A
        response = client.post(url_for('voting.cast_vote', period_id=period_id, list_id=lista_id), follow_redirects=True)
        
        # Validar UI
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Tu voto ha sido registrado' in html
        
        # === VALIDACIÓN ESTRICTA DE BACKEND: LEY DE VOTO SECRETO ===
        with app.app_context():
            # 1. El voto se guardó para la lista, pero NO tiene ID de votante
            vote = Vote.query.filter_by(election_period_id=period_id).first()
            assert vote is not None
            assert vote.candidate_list_id == lista_id
            assert not hasattr(vote, 'voter_id') # El modelo Vote NO debe tener referencia al votante
            
            # 2. El votante fue marcado como "Ya votó" en la tabla Participation
            participation = VoterParticipation.query.filter_by(voter_id=voter_id, election_period_id=period_id).first()
            assert participation is not None
            assert not hasattr(participation, 'candidate_list_id') # Participation NO debe saber por quién votó

def test_prevent_double_voting(client, app, setup_election):
    """Comprueba que un estudiante no pueda votar dos veces."""
    period_id = setup_election['period'].id
    lista_id = setup_election['lista_a'].id
    
    with client:
        client.post(url_for('auth.login'), data={'username': '0999999999', 'password': 'testpassword'}, follow_redirects=True)
        
        # Primer Voto
        client.post(url_for('voting.cast_vote', period_id=period_id, list_id=lista_id), follow_redirects=True)
        
        # Segundo Voto Inmediato
        response = client.post(url_for('voting.cast_vote', period_id=period_id, list_id=lista_id), follow_redirects=True)
        
        # Validar UI rechazo
        html = response.data.decode('utf-8')
        assert 'Ya has votado' in html
        
        # Validar BD puramente backend (Solo existe 1 voto)
        with app.app_context():
            total_votes = Vote.query.filter_by(election_period_id=period_id).count()
            assert total_votes == 1
