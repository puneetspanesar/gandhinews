"""Compose a Gandhi News story picture from 1-3 source images.

Usage (from code): compose(paths, out_base, focus=None)
 - paths: list of image paths (1, 2 or 3)
 - out_base: path without suffix; writes {out_base}-1280.jpg and -640.jpg (4:3)
 - focus: optional list of (fx, fy) per image, 0-1, to override face detection

One image: a straight 4:3 crop, face-aware.
Two or three images: side-by-side panels split by a thin white gutter, each panel
cropped around the largest face found (or the given focus point), so the people in
the story are framed the way news sites frame them.
"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageOps

W, H, GUT = 1280, 960, 6
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def faces(im):
    g = cv2.cvtColor(np.array(im.convert('RGB')), cv2.COLOR_RGB2GRAY)
    s = 900 / max(g.shape)
    small = cv2.resize(g, None, fx=s, fy=s) if s < 1 else g
    k = s if s < 1 else 1
    fs = CASCADE.detectMultiScale(small, scaleFactor=1.1, minNeighbors=6, minSize=(24, 24))
    return [(x / k, y / k, w / k, h / k) for (x, y, w, h) in fs]


def crop_panel(im, pw, ph, focus=None):
    """Crop im to aspect pw:ph around the main face (or focus), return resized panel.
    focus='fit' places the whole image (a logo) centred on its own background colour."""
    iw, ih = im.size
    if focus == 'fit':
        bg = im.getpixel((2, 2))
        panel = Image.new('RGB', (pw, ph), bg)
        # Trim the empty margin around the logo first.
        diff = np.abs(np.asarray(im, dtype=int) - np.array(bg)).sum(axis=2) > 40
        ys, xs = np.where(diff)
        if len(xs):
            im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        t = im.copy(); t.thumbnail((int(pw * 0.9), int(ph * 0.6)), Image.LANCZOS)
        panel.paste(t, ((pw - t.width) // 2, (ph - t.height) // 2))
        return panel
    ar = pw / ph
    fx = fy = None
    zoom_face = None
    if focus:
        fx, fy = focus[0] * iw, focus[1] * ih
        if len(focus) > 2:
            zoom_face = focus[2] * ih * 0.26 / 1.0  # third value: crop height as a share of the image
    else:
        f = faces(im)
        if f:
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            fx, fy, zoom_face = x + w / 2, y + h / 2, h
    # Largest crop of the right aspect that fits.
    cw, ch = (iw, iw / ar) if iw / ar <= ih else (ih * ar, ih)
    if zoom_face:
        # Tighten so the face is about a quarter of the panel height, never smaller than 45% of the image.
        target = zoom_face / 0.26
        if target < ch:
            s = max(target / ch, 0.45)
            cw, ch = cw * s, ch * s
    if fx is None:
        fx, fy = iw / 2, ih * 0.42
    x0 = min(max(fx - cw / 2, 0), iw - cw)
    # Put the face about 38% down the panel.
    y0 = min(max(fy - ch * 0.38, 0), ih - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((pw, ph), Image.LANCZOS)


def compose(paths, out_base, focus=None, weights=None):
    ims = [ImageOps.exif_transpose(Image.open(p)).convert('RGB') for p in paths]
    n = len(ims)
    focus = focus or [None] * n
    canvas = Image.new('RGB', (W, H), 'white')
    if n == 1:
        canvas.paste(crop_panel(ims[0], W, H, focus[0]), (0, 0))
    else:
        avail = W - GUT * (n - 1)
        weights = weights or [1] * n
        x = 0
        for i, im in enumerate(ims):
            w = int(avail * weights[i] / sum(weights)) if i < n - 1 else W - x
            canvas.paste(crop_panel(im, w, H, focus[i]), (x, 0))
            x += w + GUT
    canvas.save(f'{out_base}-1280.jpg', quality=84, optimize=True, progressive=True)
    canvas.resize((640, 480), Image.LANCZOS).save(f'{out_base}-640.jpg', quality=82, optimize=True, progressive=True)


if __name__ == '__main__':
    compose(sys.argv[2:], sys.argv[1])
