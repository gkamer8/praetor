from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for


bp = Blueprint('view', __name__, url_prefix='/view')

@bp.route('/', methods=('GET',))
def register():
    return render_template('view.html')