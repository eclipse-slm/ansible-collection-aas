import re


def get_id_short(id_short, level_key=''):
    if id_short is None:
        return id_short

    if level_key is None:
        level_key = ''

    no_special_chars = re.sub('[^a-zA-Z0-9_]', '', id_short)
    no_letter_at_start_pattern = re.compile('^[^a-zA-Z].*$')

    # if id short has no letter as first char and level_key is defined:
    if no_letter_at_start_pattern.match(no_special_chars) and len(level_key) > 0:
        # append level key to idshort
        return f'{level_key}_{no_special_chars}'
    else:
        # replace all chars not being a letter:
        return re.sub(r'^[^a-zA-Z]*', '', no_special_chars)