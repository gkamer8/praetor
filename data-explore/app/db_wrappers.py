"""

All functions that depend on the peculiarities of the database

"""

def add_example(db, input_dict):
    txt = input_dict['completion']
    tags = input_dict['tags']
    prompt_id = input_dict['prompt_id']
    db.execute("INSERT INTO examples (completion, tags, prompt_id) VALUES (?, ?, ?)", (txt, tags, prompt_id))
    db.commit()

