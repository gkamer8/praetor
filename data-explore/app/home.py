from flask import (
    Blueprint,
    render_template,
    request
)
from app.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=('GET',))
def home(): 
    return render_template('home.html')


@bp.route('/manifest', methods=('GET',))
def manifest():
    db = get_db()
    prompts = db.execute(
        'SELECT * FROM prompts'
    ).fetchall()

    print(prompts)

    return render_template('manifest.html', prompts=prompts)