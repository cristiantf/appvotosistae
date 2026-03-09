from flask import Blueprint

bp = Blueprint('voting', __name__, template_folder='templates')

from src.voting import routes
