from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)
from app.db import get_db
from app.db_wrappers import add_prompt, add_bulk
import json

bp = Blueprint('add', __name__)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    
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
            return redirect(f"/manifest")
        else:
            prompt = request.form.get("prompt")
            style = request.form.get("style")
            tags = request.form.get("tags")
            db = get_db()
            id = add_prompt(db, {'prompt': prompt, 'style': style, 'tags': tags})
            return redirect(f"/view?prompt_id={id}")


    return render_template('add.html')