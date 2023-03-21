from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)
from app.db import get_db
from app.db_wrappers import add_prompt

bp = Blueprint('add', __name__)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    
    if request.method == "POST":
        prompt = request.form.get("prompt")
        style = request.form.get("style")
        tags = request.form.get("tags")
        db = get_db()
        id = add_prompt(db, {'prompt': prompt, 'style': style, 'tags': tags})
        return redirect(f"/view?prompt_id={id}")


    return render_template('add.html')