
"""

Utility functions

"""

def tag_string_to_list(tags):
    if not tags:
        return []
    return [tag for tag in tags.replace(" ", "").split(",") if tag]
