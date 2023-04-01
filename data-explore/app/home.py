from flask import (
    Blueprint,
    render_template,
    request
)
from app.db import get_db
from app.db_wrappers import search_prompts
from app.utils import tag_string_to_list

bp = Blueprint('home', __name__)

@bp.route('/', methods=('GET',))
def home(): 
    return render_template('home.html')


@bp.route('/manifest', methods=('GET', 'POST'))
def manifest():

    db = get_db()

    limit = 100
    offset = request.args.get('offset')
    if not offset:
        offset = 0

    content_arg = request.args.get("content")
    example_arg = request.args.get("example")
    tags_arg = request.args.get("tags")
    tags_arg = tag_string_to_list(tags_arg)

    prompts, total_results = search_prompts(db, limit, offset, content_arg, example_arg, tags_arg)

    return render_template('manifest.html', prompts=prompts, page_size=limit, total_results=total_results)