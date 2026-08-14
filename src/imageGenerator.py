"""
imageGenerator.py - Generador de imagenes BMP de dialogo (Project Nomads 2002)

Lee los archivos locale.json de la carpeta `i18n` y genera una imagen BMP por
cada dialogo dentro de `img_locale`, respetando la misma estructura de carpetas:

    i18n/es/chapter01/part00/locale.json
        -> img_locale/es/chapter01/part00/omu_c01p00_basaltface01.bmp
        -> img_locale/es/chapter01/part00/omu_c01p00_basaltface02.bmp

COMO EJECUTARLO
---------------
1) Requisitos: Python 3.x y la libreria Pillow:
       pip install pillow
2) Desde la carpeta `src`:
       python imageGenerator.py
3) Las imagenes quedan en `src/img_locale/...`.

Para anadir mas capitulos o partes, basta con crear los locale.json con la
misma estructura en `i18n` y volver a ejecutar el script.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ===== Rutas =====
SCRIPT_DIR = Path(__file__).resolve().parent  # carpeta donde vive este script
I18N_ROOT = SCRIPT_DIR / "i18n"               # textos de entrada
IMG_ROOT = SCRIPT_DIR / "img_locale"          # imagenes de salida

# ===== Configuracion de estilo =====
BG_COLOR = (0, 0, 0)            # Negro
TEXT_COLOR = (255, 255, 255)    # Blanco
FONT_SIZE = 16                  # Tamano de letra (px)
MAX_LINES = 2                   # Maximo de lineas de texto
MIN_FONT_SIZE = 11              # Si aun asi no cabe, se reduce la fuente hasta este minimo
LINE_SPACING = 5                # Separacion entre lineas (px)
IMG_W = 512                     # Ancho fijo de la imagen (px)
IMG_H = 50                      # Alto fijo de la imagen (px)
MARGIN_X = 20                   # Margen horizontal (texto no debe superar IMG_W - 2*MARGIN_X)

# El texto nunca podra superar este ancho, asi cabe dentro de la imagen fija
MAX_CONTENT_W = IMG_W - 2 * MARGIN_X

# Fuentes sans-serif legibles (en orden de preferencia)
FONT_CANDIDATES = [
    "segoeui.ttf",     # Segoe UI
    "verdana.ttf",     # Verdana (Windows)
    "tahoma.ttf",      # Tahoma (Windows)
    "trebuc.ttf",      # Trebuchet MS (Windows)
    "dejavusans.ttf",  # DejaVu Sans (Linux)
]


def load_font(size):
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ink_bbox(draw, text, font):
    """Bbox de la tinta real, relativo a la linea base (anchor 'ls'): top<0, bottom>0."""
    return draw.textbbox((0, 0), text, font=font, anchor="ls")


def text_size(draw, text, font):
    bbox = ink_bbox(draw, text, font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def greedy_wrap(draw, paragraph, font, max_w):
    """Parte un parrafo en lineas que quepan en max_w (palabra a palabra)."""
    words = paragraph.split()
    if not words:
        return [""]
    if text_size(draw, paragraph, font)[0] <= max_w:
        return [paragraph]
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if text_size(draw, candidate, font)[0] <= max_w:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def balanced_two_lines(draw, words, font, max_w):
    """Reparte las palabras en exactamente 2 lineas lo mas equilibradas posible."""
    best = None
    best_cost = None
    for i in range(len(words) - 1):
        line1 = " ".join(words[:i + 1])
        line2 = " ".join(words[i + 1:])
        w1 = text_size(draw, line1, font)[0]
        w2 = text_size(draw, line2, font)[0]
        overflow = max(0, w1 - max_w) + max(0, w2 - max_w)
        cost = overflow * 100000 + abs(w1 - w2)
        if best_cost is None or cost < best_cost:
            best = [line1, line2]
            best_cost = cost
    return best


def wrap_text(draw, text, font, max_w, max_lines=2):
    """Devuelve la lista de lineas: 1 linea si cabe, 2 lineas centradas si no."""
    flat = text.replace("\n", " ")
    if text_size(draw, flat, font)[0] <= max_w:
        return [flat]

    # Respetar saltos \n manuales cuando sea posible
    lines = []
    for para in text.split("\n"):
        lines.extend(greedy_wrap(draw, para, font, max_w))

    # Si son demasiadas lineas, reorganizar en exactamente max_lines equilibradas
    if len(lines) > max_lines:
        lines = balanced_two_lines(draw, text.split(), font, max_w)
    return lines


def compute_layout(text):
    """Ajusta el tamano de fuente hasta que el texto quepa en MAX_LINES lineas."""
    size = FONT_SIZE
    lines, font = [], ImageFont.load_default()
    while size >= MIN_FONT_SIZE:
        font = load_font(size)
        dummy = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy)
        lines = wrap_text(draw, text, font, MAX_CONTENT_W, MAX_LINES)
        if all(text_size(draw, line, font)[0] <= MAX_CONTENT_W for line in lines):
            return lines, font
        size -= 1
    return lines, font


def create_bmp_with_text(filename, text):
    lines, font = compute_layout(text)

    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    boxes = [ink_bbox(draw, line, font) for line in lines]
    line_inks = [b[3] - b[1] for b in boxes]

    img = Image.new("RGB", (IMG_W, IMG_H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    total_h = sum(line_inks) + LINE_SPACING * (len(lines) - 1)
    y = (IMG_H - total_h) / 2
    for line, (l, t, r, b) in zip(lines, boxes):
        baseline = y - t
        x = (IMG_W - (r - l)) / 2 - l
        draw.text((x, baseline), line, fill=TEXT_COLOR, font=font, anchor="ls")
        y += (b - t) + LINE_SPACING

    img.save(filename)
    print(f"Creado: {filename}  [{IMG_W}x{IMG_H}]")


def render_locale_json(json_path):
    """Genera las imagenes de un locale.json en img_locale con la misma estructura."""
    rel = json_path.relative_to(I18N_ROOT)   # ej: es/chapter01/part00/locale.json
    out_dir = IMG_ROOT / rel.parent          # ej: img_locale/es/chapter01/part00
    out_dir.mkdir(parents=True, exist_ok=True)

    # utf-8-sig por si el JSON trae BOM
    with open(json_path, "r", encoding="utf-8-sig") as fh:
        translations = json.load(fh)

    for name, text in translations.items():
        if isinstance(text, str):
            create_bmp_with_text(out_dir / name, text)


def main():
    json_files = sorted(I18N_ROOT.rglob("*.json"))
    if not json_files:
        print(f"No se encontraron archivos locale.json en: {I18N_ROOT}")
        return 1

    for json_path in json_files:
        render_locale_json(json_path)

    print(f"\n¡Proceso completado! Se generaron las imagenes en {IMG_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
