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

    content_arg = request.args.get("content")
    style_arg = request.args.get("style")
    example_arg = request.args.get("example")

    if content_arg:
        content = "%" + content_arg + "%"
    if style_arg:
        style = "%" + style_arg + "%"
    
    if example_arg:
        example = "%" + example_arg + "%"
        sql = "SELECT * FROM prompts WHERE prompt LIKE ? AND style LIKE ? AND EXISTS (SELECT * FROM examples WHERE examples.prompt_id = prompts.id AND examples.completion LIKE ?)"
        prompts = db.execute(
            sql, (content, style, example)
        ).fetchall()
    else:
        prompts = db.execute(
            'SELECT * FROM prompts WHERE prompt LIKE ? AND style LIKE ?', (content, style)
        ).fetchall()

    return render_template('manifest.html', prompts=prompts)