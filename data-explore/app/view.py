from flask import (
    Blueprint,
    redirect,
    render_template,
    request
)
from app.db import get_db
from app.db_wrappers import add_or_update_example, delete_example, get_examples_by_prompt_id, get_prompt_by_id, get_prompt_values_by_prompt_id, get_style_by_id, get_tags_by_prompt_id, update_prompt, delete_prompt

bp = Blueprint('view', __name__)

@bp.route('/view', methods=('GET', 'POST'))
def view():

    prompt_id = request.args.get("prompt_id")

    db = get_db()

    if request.method == "POST":

        prompt = request.form.get('prompt')
        tags = request.form.get("tags")
        id = request.form.get("id")
        style = request.form.get('style')
        txt = request.form.get("completion")

        prompt_or_example = request.form.get("prompt_or_example")
        if prompt_or_example == 'prompt':
            # Am I deleting?
            if not (tags or style or prompt):
                delete_prompt(db, {'id': id})
            else:
                inputs = {
                    'prompt': prompt,
                    'tags': tags,
                    'id': id,
                    'style': style
                }
                update_prompt(db, inputs)
        elif prompt_or_example == 'example':
            txt = request.form.get("completion")
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

    prompt_dict = get_prompt_by_id(get_db(), prompt_id)
    tags = get_tags_by_prompt_id(get_db(), prompt_id)
    prompt_values = get_prompt_values_by_prompt_id(get_db(), prompt_id)
    completions = get_examples_by_prompt_id(get_db(), prompt_id)
    style = get_style_by_id(get_db(), prompt_dict['style'])

    return render_template('view.html', prompt=prompt_dict, style=style, prompt_values=prompt_values, prompt_tags=tags, completions=completions)