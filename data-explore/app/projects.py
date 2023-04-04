from flask import (
    Blueprint,
    render_template,
    request
)
from app.db import get_db
from app.db_wrappers import get_projects, get_project_by_id, get_styles_by_project_id, add_project

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=('GET', 'POST'))
def projects():

    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        add_project(get_db(), name, description)

    projects = get_projects(get_db())
    return render_template('projects.html', projects=projects)

@bp.route('/project', methods=('GET',))
def project():
    project_id = request.args.get("id")
    project = get_project_by_id(get_db(), project_id)
    styles = get_styles_by_project_id(get_db(), project_id)
    return render_template('project.html', project=project, styles=styles)
