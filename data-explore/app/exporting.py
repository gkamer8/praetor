import os
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    send_file,
    current_app
)
from app.db import get_db
from app.db_wrappers import export, get_exports, get_export_by_id

bp = Blueprint('exporting', __name__)

@bp.route('/export', methods=('GET', 'POST'))
def exp():
    if request.method == "POST":
        filename = request.form.get('filename') if request.form.get('filename') else "export.json"

        tags = request.form.get('tags')
        content = request.form.get('content')
        style = request.form.get('style')
        completion_key = request.form.get('completion_key')
        prompt_key = request.form.get('prompt_key')

        export(get_db(), filename=filename, tags=tags, content=content, style=style, completion_key=completion_key, prompt_key=prompt_key)
        return redirect("/tasks")

    return render_template('export.html')

@bp.route('/exports', methods=('GET',))
def exps():
    download_id = request.args.get('download_id')
    db = get_db()
    if download_id:
        row = get_export_by_id(db, download_id)
        path = os.path.join(current_app.config.get('EXPORTS_PATH'), row['filename'])
        return send_file(path, as_attachment=True)

    exports = get_exports(db)
    
    return render_template('exports.html', exports=exports)
