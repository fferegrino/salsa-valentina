def relative2absolute(cx, cy, w, h, img_w, img_h, dtype='int'):
    pcx = (cx - w / 2) * img_w
    pcy = (cy - h / 2) * img_h
    width = w * img_w
    height = h * img_h
    if dtype == 'int':
        return int(pcx), int(pcy), int(width), int(height)
    return pcx, pcy, width, height


item_template = """item {{
    id: {class_id}
    name: '{name}'
}}
"""


def generate_label_map(labels):
    return '\n'.join([
        item_template.format(class_id=int(k), name=v) for k, v in labels.items()
    ])
