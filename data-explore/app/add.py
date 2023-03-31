from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)
from app.db import get_db
from app.db_wrappers import add_prompt, add_bulk, get_project_by_id, get_style_by_id, get_styles_by_project_id, get_keys_by_style_id
import json

bp = Blueprint('add', __name__)

@bp.route('/add', methods=('GET', 'POST'))
def add():

    db = get_db()

    if request.method == "POST":

        # Was it a bulk upload?
        file = request.files.get('file')
        if file:
            file_contents = file.read()
            # Read as json
            # btw this is probably a security vulnerability
            # Probably should check for filesize as well
            data = json.loads(file_contents)

            # Optional
            key_tags = request.form.get("key_tags")
            if not key_tags:
                key_tags = None
            options = {
                'key_completion': request.form.get("key_completion"),
                'key_prompt': request.form.get("key_prompt"),
                'key_tags': request.form.get("key_tags"),
                'tags': request.form.get("tags"),
                'style': request.form.get("style"),
            }
            add_bulk(get_db(), data, options)
            return redirect("/tasks")
        else:
            project_id = request.form.get('project_id')
            style_id = request.form.get('style_id')

            style_keys = get_keys_by_style_id(db, style_id)
            style = get_style_by_id(db, style_id)

            # don't need completion key for style_keys
            if 'completion_key' in style:
                completion_key = style['completion_key']
                style_keys = [x for x in style_keys if x['name'] != completion_key]

            keys = {x['name']: request.form.get("key." + x['name']) for x in style_keys}
            tags = request.form.get("tags")
            if tags:
                tags = tags.replace(" ", "").split(",")
            else:
                tags = []
            id = add_prompt(db, keys=keys, tags=tags, project_id=project_id, style_id=style_id)
            return redirect(f"/view?prompt_id={id}")
    else:
        project_id = request.args.get('project_id')
        style_id = request.args.get('style_id')

        style = get_style_by_id(db, style_id)
        project = get_project_by_id(db, project_id)
        style_keys = get_keys_by_style_id(db, style_id)
        # don't need completion key for style_keys
        if 'completion_key' in style:
            completion_key = style['completion_key']
            style_keys = [x for x in style_keys if x['name'] != completion_key]

        return render_template('add.html', style=style, project=project, style_keys=style_keys)