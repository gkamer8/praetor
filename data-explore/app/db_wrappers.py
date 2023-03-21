"""

All functions that depend on the peculiarities of the database

"""

# Adds example to database and returns that example's id
def add_example(db, input_dict):
    txt = input_dict['completion']
    tags = input_dict['tags']
    prompt_id = input_dict['prompt_id']
    c = db.cursor()
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
            db.commit()
        
        # Now add example
        txt = item[key_completion]
        tags = options['tags'] + (("," + item[key_tags]) if key_tags else "")
        c.execute("INSERT INTO examples (completion, tags, prompt_id) VALUES (?, ?, ?)", (txt, tags, row_id))
        db.commit()
