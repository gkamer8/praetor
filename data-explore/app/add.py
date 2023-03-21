from flask import (
    Blueprint,
    render_template,
    request
)
from app.db import get_db

bp = Blueprint('add', __name__)

@bp.route('/add', methods=('GET', 'POST'))
def manifest():
    return render_template('add.html')