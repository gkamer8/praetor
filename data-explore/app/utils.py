
"""

Utility functions

"""

def tag_string_to_list(tags):
    return [tag for tag in tags.replace(" ", "").split(",") if tag]
