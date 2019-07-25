def relative2absolute(cx, cy, w, h, img_w, img_h):
    pcx = (cx - w/2) * img_w
    pcy = (cy - h/2) * img_h
    width = w * img_w
    height = h * img_h
    return pcx, pcy, width, height