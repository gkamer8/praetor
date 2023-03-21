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
    c.commit()
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
