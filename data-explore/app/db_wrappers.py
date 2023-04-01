import multiprocessing
import json
import os
from app.db import SQLiteJSONEncoder
from flask import current_app

"""

All functions that depend on the peculiarities of the database

"""

# EXAMPLES

def add_example(db, prompt_id, completion, tags):
    c = db.cursor()
    c.execute("INSERT INTO examples (completion, prompt_id) VALUES (?, ?)", (completion, prompt_id))
    item_id = c.lastrowid
    
    # Add tags
    for tag in tags:
        c.execute("INSERT INTO tags (example_id, value) VALUES (?, ?)", (item_id, tag))
    db.commit()
    return item_id


def delete_example(db, example_id):
    db.execute("DELETE FROM examples WHERE id = ?", (example_id,))
    db.commit()


def update_example(db, example_id, completion, tags):
    c = db.cursor()

    # Remove all tags
    c.execute("DELETE FROM tags WHERE example_id = ?", (example_id,))
    # Update text
    c.execute("UPDATE examples SET completion = ? WHERE id = ?", (completion, example_id))
    for t in tags:
        c.execute("INSERT INTO tags (example_id, value) VALUES (?, ?)", (example_id, t))
    db.commit()
    return example_id


# PROMPTS

def delete_prompt(db, prompt_id):

    # Remove all tags
    # Remove all prompt_values
    # remove associated examples

    db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    db.execute("DELETE FROM tags WHERE prompt_id = ?", (prompt_id,))
    db.execute("DELETE FROM prompt_values WHERE prompt_id = ?", (prompt_id,))
    db.execute("DELETE FROM examples WHERE prompt_id = ?", (prompt_id,))
    db.commit()

def update_prompt(db, prompt_id, prompt_values, tags):
    c = db.cursor()

    # Update prompt values
    for key in prompt_values:
        sql = """
            UPDATE prompt_values SET value = ? WHERE prompt_id = ? AND key = ?
        """
        c.execute(sql, (prompt_values[key], prompt_id, key))
    # Update tags
    # Remove all prior tags
    sql = """
        DELETE FROM tags
        WHERE prompt_id = ?
    """
    c.execute(sql, (prompt_id,))
    for tag in tags:
        c.execute("INSERT INTO tags (value, prompt_id) VALUES (?, ?)", (tag, prompt_id))

    db.commit()
    return prompt_id

# Adds prompt to database and returns that prompt's id
def add_prompt(db, **kwargs):

    tags = kwargs['tags']
    keys = kwargs['keys']
    project_id = kwargs['project_id']
    style_id = kwargs['style_id']

    c = db.cursor()

    c.execute("INSERT INTO prompts (project_id, style) VALUES (?, ?)", (project_id, style_id))
    prompt_id = c.lastrowid

    for t in tags:
        c.execute("INSERT INTO tags (value, prompt_id) VALUES (?, ?)", (t, prompt_id))

    for k in keys:
        c.execute("INSERT INTO prompt_values (prompt_id, key, value) VALUES (?, ?, ?)", (prompt_id, k, keys[k]))

    db.commit()
    return prompt_id

# Takes data and inserts prompts and examples
# Data is a list of dictionaries 
"""
options takes:
- (optional) tags (additional tags to append to each prompt and example)
- (required) style (for the prompts)
- (required) key_continuation (what key to use for the coninuation)
- (required) key_prompt (what key to use for the prompt)
- (optional) key_tags (what key to use for both prompt and example tags)
"""
def add_bulk(db, data, options):
    p = multiprocessing.Process(target=add_bulk_background, args=(db, data, options))
    p.start()

    sql = """
        INSERT INTO tasks (`type`, `status`, `pid`)
        VALUES ("bulk_upload",
                "in_progress",
                ?
                );
    """
    db.execute(sql, (p.pid,))
    db.commit()
    status = {
        'pid': p.pid,
        'status': 'in_progress'
    }
    return status


def add_bulk_background(db, data, options):
    try:
        key_completion = options['key_completion']
        key_prompt = options['key_prompt']
        key_tags = None if 'key_tags' not in options else options['key_tags']
        style = options['style']
        c = db.cursor()
        for item in data:
            prompt = item[key_prompt]
            existing_prompt = c.execute(
                'SELECT * FROM prompts WHERE prompt LIKE ?', (prompt,)
            ).fetchone()
            
            if existing_prompt:
                row_id = c.lastrowid
            else:
                tags = options['tags'] + (("," + item[key_tags]) if key_tags else "")
                c.execute("INSERT INTO prompts (prompt, tags, style) VALUES (?, ?, ?)", (prompt, tags, style))
                row_id = c.lastrowid
            
            # Now add example
            txt = item[key_completion]
            tags = options['tags'] + (("," + item[key_tags]) if key_tags else "")
            c.execute("INSERT INTO examples (completion, tags, prompt_id) VALUES (?, ?, ?)", (txt, tags, row_id))
            db.commit()

        sql = """
            UPDATE tasks
            SET status = 'completed'
            WHERE pid = ?;
        """
        db.execute(sql, (os.getpid(),))
        db.commit()
    except:
        sql = """
            UPDATE tasks
            SET status = 'failed'
            WHERE pid = ?;
        """
        db.execute(sql, (os.getpid(),))
        db.commit()


def get_search_query(count_only=False, include_examples=False, columns_str="*", **kwargs):
    
    content = "%"
    style = "%"
    tags = "%"
    example = "%"

    find_example1 = ""
    find_example2 = ""
    if 'content' in kwargs and kwargs['content']:
        content = "%" + kwargs['content'] + "%"
    if 'style' in kwargs and kwargs['style']:
        style = "%" + kwargs['style'] + "%"
    if 'tags' in kwargs and kwargs['tags']:
        tags = "%" + kwargs['tags'] + "%"

    args = [content, style, tags]

    search_for_example = ('example' in kwargs and kwargs['example'])
    if include_examples or search_for_example:
        if search_for_example:
            example = "%" + kwargs['example'] + "%"
        find_example1 = """JOIN examples AS e
                ON p.id = e.prompt_id"""
        find_example2 = "AND e.completion LIKE ?"
        args.append(example)

    limit_str = ""
    offset_str = ""
    if not count_only and 'limit' in kwargs and kwargs['limit']:
        args.append(kwargs['limit'])
        limit_str = f"LIMIT ?"
    if not count_only and 'offset' in kwargs and kwargs['offset']:
        args.append(kwargs['offset'])
        offset_str = f"OFFSET ?"
    
    
    columns = "COUNT(*) as nresults" if count_only else columns_str
    sql = f"""SELECT {columns}
                FROM prompts AS p
                {find_example1}
                WHERE p.prompt LIKE ? 
                AND p.style LIKE ? 
                AND p.tags LIKE ? 
                {find_example2}
                {limit_str}
                {offset_str}
            """
    return sql, args


def export(db, **kwargs):
    p = multiprocessing.Process(target=export_background, args=(db,), kwargs=kwargs)
    p.start()

    sql = """
        INSERT INTO tasks (`type`, `status`, `pid`)
        VALUES ("export",
                "in_progress",
                ?
                );
    """
    db.execute(sql, (p.pid,))
    db.commit()
    status = {
        'pid': p.pid,
        'status': 'in_progress'
    }
    return status


def export_background(db, **kwargs):
    try:
        # Note: once this gets updated to remove get_search_query, that function becomes unused
        sql, args = get_search_query(include_examples=True,
                                    columns_str="p.prompt AS prompt, e.completion AS completion",
                                    **kwargs)

        cursor = db.cursor()
        # Execute query
        cursor.execute(sql, args)

        filename = kwargs['filename']
        path = os.path.join(current_app.config.get('EXPORTS_PATH'), filename)


        completion_key = kwargs['completion_key'] if 'completion_key' in kwargs else "output"
        prompt_key = kwargs['prompt_key'] if 'prompt_key' in kwargs else "instruction"

        fhand = open(path, 'w')
        fhand.write('[\n')

        encoder = SQLiteJSONEncoder(indent=4)
        row = cursor.fetchone()
        while row is not None:
            # Serialize row to JSON and write to file
            row = {prompt_key: row['prompt'], completion_key: row['completion']}
            json_data = encoder.encode(row)

            fhand.write(json_data)

            # Get next row
            row = cursor.fetchone()

            # If there are more rows, write a comma after the previous row
            if row is not None:
                fhand.write(',\n')

        fhand.write(']')
        fhand.close()

        sql = """
                INSERT INTO exports (`filename`)
                VALUES (?);
            """
        db.execute(sql, (filename,))

        sql = """
                UPDATE tasks
                SET status = 'completed'
                WHERE pid = ?;
            """
        db.execute(sql, (os.getpid(),))
        db.commit()

    except Exception as e:
        sql = """
            UPDATE tasks
            SET status = 'failed'
            WHERE pid = ?;
        """
        db.execute(sql, (os.getpid(),))
        db.commit()
        print(f"Error occurred: {e}")

def search_prompts(db, limit, offset, content_arg, example_arg, tags_arg):
    
    offset = 0 if not offset else offset
    limit = 100 if not limit else limit
    content_arg = "%" if not content_arg else "%" + content_arg + "%"
    
    x = "" if example_arg else "LEFT"
    example_arg = "%" if not example_arg else "%" + example_arg + "%"

    args = [example_arg]

    tag_query_str = ""
    if tags_arg:
        tag_query_str = f"JOIN tags ON prompts.id = tags.prompt_id AND ("
        for i, tag in enumerate(tags_arg):
            tag_query_str += f"tags.value LIKE ?"
            args.append(tag)
            if i < len(tags_arg) - 1:
                tag_query_str += " OR "
        tag_query_str += ")"

    args.extend([content_arg, limit, offset])

    sql = f"""
        WITH main_search AS
        (
            SELECT DISTINCT prompts.*, prompt_values.*, COUNT(*) OVER() AS total_results
            FROM prompts
            JOIN prompt_values ON prompts.id = prompt_values.prompt_id
            JOIN styles ON prompts.style = styles.id AND prompt_values.key = styles.preview_key
            {x} JOIN examples ON prompts.id = examples.prompt_id AND examples.completion LIKE ?
            {tag_query_str}
            WHERE prompt_values.value LIKE ?
            LIMIT ?
            OFFSET ?
        )
        SELECT main_search.*, GROUP_CONCAT(t.value) AS tags
        FROM main_search
        LEFT JOIN tags t ON main_search.prompt_id = t.prompt_id
        GROUP BY main_search.id
    """

    results = db.execute(sql, tuple(args))
    fetched = results.fetchall()
    total_results = 0 if len(fetched) == 0 else fetched[0]['total_results']
    return fetched, total_results


def get_tasks(db):
    sql = """
        SELECT * FROM tasks ORDER BY created_at DESC
    """
    tasks = db.execute(sql)
    return tasks

def get_exports(db):
    sql = """
        SELECT * FROM exports ORDER BY created_at DESC
    """
    exports = db.execute(sql)
    return exports

def get_export_by_id(db, id):
    sql = """
        SELECT * FROM exports WHERE id = ?
    """
    export = db.execute(sql, id)
    return export.fetchone()

def get_prompt_by_id(db, id):
    sql = """
        SELECT * FROM prompts WHERE id = ?
    """
    prompt = db.execute(sql, (id,))
    return prompt.fetchone()

def get_examples_by_prompt_id(db, prompt_id, with_tags=True):
    if with_tags:
        sql = """
        SELECT e.*, GROUP_CONCAT(t.value) AS tags
        FROM examples e
        LEFT JOIN tags t ON e.id = t.example_id
        WHERE e.prompt_id = ?
        GROUP BY e.id
        """
    else:
        sql = """
            SELECT * FROM examples WHERE prompt_id = ?
        """
    examples = db.execute(sql, (prompt_id,))
    return examples.fetchall()

def get_projects(db):
    sql = """
        SELECT * FROM projects
    """
    examples = db.execute(sql)
    return examples.fetchall()

def get_project_by_id(db, id):
    sql = """
        SELECT * FROM projects WHERE id = ?
    """
    examples = db.execute(sql, (id,))
    return examples.fetchone()

def get_styles_by_project_id(db, id):
    sql = """
        SELECT * FROM styles WHERE project_id = ?
    """
    examples = db.execute(sql, (id,))
    return examples.fetchall()

def get_style_by_id(db, id):
    sql = """
        SELECT * FROM styles WHERE id = ?
    """
    style = db.execute(sql, (id,))
    return style.fetchone()

def get_keys_by_style_id(db, id):
    sql = """
        SELECT * FROM style_keys WHERE style_id = ?
    """
    keys = db.execute(sql, (id,))
    return keys.fetchall()

def get_tags_by_prompt_id(db, prompt_id):
    sql = """
        SELECT * FROM tags WHERE prompt_id = ?
    """
    tags = db.execute(sql, (prompt_id,))
    return tags.fetchall()

def get_prompt_values_by_prompt_id(db, prompt_id):
    sql = """
        SELECT * FROM prompt_values WHERE prompt_id = ?
    """
    vals = db.execute(sql, (prompt_id,))
    return vals.fetchall()