from flask import (
    Blueprint,
    redirect,
    render_template,
    request
)
from app.db import get_db
from app.db_wrappers import export, get_exports

bp = Blueprint('exporting', __name__)

@bp.route('/export', methods=('GET', 'POST'))
def exp():
    if request.method == "POST":
        export(get_db())
        return redirect("/tasks")

    return render_template('export.html')

@bp.route('/exports', methods=('GET',))
def exps():
    exports = get_exports(get_db())
    print(exports)
    return render_template('exports.html', exports=exports)
