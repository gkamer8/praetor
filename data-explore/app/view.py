from flask import (
    Blueprint,
    render_template,
    request
)
from app.db import get_db
from app.db_wrappers import add_or_update_example, delete_example

bp = Blueprint('view', __name__)

def report_error(message):
    return f"Error: {message}"

@bp.route('/view', methods=('GET', 'POST'))
def view():

    prompt_id = request.args.get("prompt_id")
    ex_id = request.args.get("example_id")

    db = get_db()

    if request.method == "POST":
        txt = request.form.get("completion")
        tags = request.form.get("tags")
        id = request.form.get("id")
        # no txt, assume it means delete
        if not txt:
            delete_example(db, {'id': id})
        else:
            inputs = {
                'completion': txt,
                'tags': tags,
                'prompt_id': prompt_id
            }
            if id:
                inputs['id'] = id
            add_or_update_example(db, inputs)

    prompt_dict = {}
    completions = []
    # If we have a prompt id, show the prompt and all matching responses
    # If we have only an example id, show that example's prompt and the completion
    if prompt_id:
        prompt = db.execute(
            'SELECT * FROM prompts WHERE id = ?', (prompt_id,)
        ).fetchone()
        if not prompt:
            report_error("Prompt not found with that id.")
        prompt_dict = prompt

        completions = db.execute(
            'SELECT * FROM examples WHERE prompt_id = ?', (prompt['id'],)
        ).fetchall()
    else:
        if not ex_id:
            return "Can't find any prompt/example with that id."

    return render_template('view.html', prompt=prompt_dict, completions=completions)