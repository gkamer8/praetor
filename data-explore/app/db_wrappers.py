import multiprocessing
import json
import os

"""

All functions that depend on the peculiarities of the database

"""

# Adds example to database and returns that example's id
def add_or_update_example(db, input_dict):
    txt = input_dict['completion']
    tags = input_dict['tags']
    prompt_id = input_dict['prompt_id']
    c = db.cursor()

    if 'id' in input_dict:
        item_id = input_dict['id']
        c.execute("UPDATE examples SET completion = ?, tags = ? WHERE id = ?", (txt, tags, item_id))
        db.commit()
    else:
        c.execute("INSERT INTO examples (completion, tags, prompt_id) VALUES (?, ?, ?)", (txt, tags, prompt_id))
        item_id = c.lastrowid
        db.commit()
    return item_id

# Adds prompt to database and returns that prompt's id
def add_prompt(db, input_dict):
    prompt = input_dict['prompt']
    tags = input_dict['tags']
    style = input_dict['style']
    c = db.cursor()
    c.execute("INSERT INTO prompts (prompt, tags, style) VALUES (?, ?, ?)", (prompt, tags, style))
    item_id = c.lastrowid
    db.commit()
    return item_id

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

def delete_example(db, inputs):
    id = inputs['id']
    db.execute("DELETE FROM examples WHERE id = ?", (id,))
    db.commit()

def search_prompts(db, limit, offset, content_arg, style_arg, example_arg, tags_arg):
    content = "%"
    style = "%"
    tags = "%"

    if content_arg:
        content = "%" + content_arg + "%"
    if style_arg:
        style = "%" + style_arg + "%"
    if tags_arg:
        tags = "%" + tags_arg + "%"

    total_results = 0

    if example_arg:
        example = "%" + example_arg + "%"
        sql = """SELECT COUNT(*) as nresults
                FROM prompts AS p
                JOIN examples AS e
                ON p.id = e.prompt_id 
                WHERE p.prompt LIKE ? 
                AND p.style LIKE ? 
                AND p.tags LIKE ? 
                AND e.completion LIKE ?
            """
        total = db.execute(
                sql, (content, style, tags, example)
            ).fetchall()
        total_results = total[0]['nresults']

        sql = """SELECT p.*
                FROM prompts AS p
                JOIN examples AS e
                ON p.id = e.prompt_id 
                WHERE p.prompt LIKE ? 
                AND p.style LIKE ? 
                AND p.tags LIKE ? 
                AND e.completion LIKE ?
                LIMIT ? OFFSET ?"""
        prompts = db.execute(
                sql, (content, style, tags, example, limit, offset)
            ).fetchall()
    else:
        total = db.execute(
            'SELECT COUNT(*) FROM prompts WHERE prompt LIKE ? AND style LIKE ? AND tags LIKE ? LIMIT ?', (content, style, tags, limit)
        ).fetchall()
        total_results = total[0]['COUNT(*)']

        prompts = db.execute(
            'SELECT * FROM prompts WHERE prompt LIKE ? AND style LIKE ? AND tags LIKE ? LIMIT ? OFFSET ?', (content, style, tags, limit, offset)
        ).fetchall()

    # total_results = prompts[0]['nresults']
    return prompts, total_results


def get_tasks(db):
    sql = """
        SELECT * FROM tasks ORDER BY created_at DESC
    """
    tasks = db.execute(sql)
    return tasks