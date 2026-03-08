from flask import Blueprint

bp = Blueprint('voto', __name__, template_folder='templates')

from src.voto import routes
