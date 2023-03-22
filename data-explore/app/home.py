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


@bp.route('/manifest', methods=('GET', 'POST'))
def manifest():

    content = "%"
    style = "%"
    db = get_db()

    if request.method == "POST":
        # content
        if request.form.get("content"):
            content = "%" + request.form.get("content") + "%"
        if request.form.get("style"):
            style = "%" + request.form.get("style") + "%"
        
        if request.form.get("example"):
            example = "%" + request.form.get("example") + "%"
            sql = "SELECT * FROM prompts WHERE prompt LIKE ? AND style LIKE ? AND EXISTS (SELECT * FROM examples WHERE examples.prompt_id = prompts.id AND examples.completion LIKE ?)"
            prompts = db.execute(
                sql, (content, style, example)
            ).fetchall()
        else:
            prompts = db.execute(
                'SELECT * FROM prompts WHERE prompt LIKE ? AND style LIKE ?', (content, style)
            ).fetchall()
    else:
        prompts = db.execute(
            "SELECT * FROM prompts"
        ).fetchall()

    return render_template('manifest.html', prompts=prompts)