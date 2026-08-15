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
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ===== Rutas =====
SCRIPT_DIR = Path(__file__).resolve().parent
I18N_ROOT = SCRIPT_DIR / "i18n"
IMG_ROOT = SCRIPT_DIR / "img_locale"


# ===== Configuracion =====
@dataclass(frozen=True)
class Config:
    # Colores
    bg_color: tuple = (0, 0, 0)
    text_color: tuple = (255, 255, 255)

    # Texto
    font_size: int = 16
    min_font_size: int = 11
    max_lines: int = 2
    line_spacing: int = 5

    # Imagen
    img_w: int = 512
    img_h: int = 50
    margin_x: int = 20

    # Fuentes sans-serif legibles (en orden de preferencia)
    font_candidates: tuple = (
        "segoeui.ttf",
        "verdana.ttf",
        "tahoma.ttf",
        "trebuc.ttf",
        "dejavusans.ttf",
    )

    @property
    def max_content_w(self):
        """Ancho maximo disponible para el texto."""
        return self.img_w - 2 * self.margin_x


CONFIG = Config()


# ===== Cache de fuentes =====
# Cada tamano de fuente se carga una sola vez.
FONT_CACHE = {}


def load_font(size):
    # Si la fuente para este tamano ya fue cargada, reutilizarla.
    if size in FONT_CACHE:
        return FONT_CACHE[size]

    for name in CONFIG.font_candidates:
        try:
            font = ImageFont.truetype(name, size)
            FONT_CACHE[size] = font
            return font
        except OSError:
            continue

    # Guardamos tambien la fuente por defecto para no volver a buscar
    # las fuentes candidatas si este tamano se solicita nuevamente.
    font = ImageFont.load_default()
    FONT_CACHE[size] = font

    return font


def ink_bbox(draw, text, font):
    """Bbox de la tinta real, relativo a la linea base (anchor 'ls')."""
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
        line1 = " ".join(words[: i + 1])
        line2 = " ".join(words[i + 1 :])

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


def compute_layout(text, draw):
    """Ajusta el tamano de fuente hasta que el texto quepa en MAX_LINES lineas."""
    size = CONFIG.font_size
    lines, font = [], ImageFont.load_default()

    while size >= CONFIG.min_font_size:
        font = load_font(size)

        lines = wrap_text(
            draw,
            text,
            font,
            CONFIG.max_content_w,
            CONFIG.max_lines,
        )

        if all(
            text_size(draw, line, font)[0] <= CONFIG.max_content_w for line in lines
        ):
            return lines, font

        size -= 1

    return lines, font


def render_text_image(lines, font, measure_draw):
    """Crea una imagen y dibuja en ella las lineas con la fuente indicada."""
    boxes = [ink_bbox(measure_draw, line, font) for line in lines]

    line_inks = [b[3] - b[1] for b in boxes]

    img = Image.new(
        "RGB",
        (CONFIG.img_w, CONFIG.img_h),
        color=CONFIG.bg_color,
    )

    draw = ImageDraw.Draw(img)

    total_h = sum(line_inks) + CONFIG.line_spacing * (len(lines) - 1)
    y = (CONFIG.img_h - total_h) / 2

    for line, (l, t, r, b) in zip(lines, boxes):
        baseline = y - t
        x = (CONFIG.img_w - (r - l)) / 2 - l

        draw.text(
            (x, baseline),
            line,
            fill=CONFIG.text_color,
            font=font,
            anchor="ls",
        )

        y += (b - t) + CONFIG.line_spacing

    return img


def create_bmp_with_text(filename, text, measure_draw):
    """Calcula el layout, renderiza el texto y guarda la imagen BMP."""
    lines, font = compute_layout(text, measure_draw)

    img = render_text_image(
        lines,
        font,
        measure_draw,
    )

    img.save(filename)
    img.close()

    print(f"Creado: {filename}  [{CONFIG.img_w}x{CONFIG.img_h}]")


def load_locale_json(json_path):
    """Lee un archivo locale.json y devuelve sus traducciones."""
    with open(json_path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def get_output_directory(json_path):
    """Obtiene la carpeta de salida correspondiente a un archivo JSON."""
    relative_path = json_path.relative_to(I18N_ROOT)
    return IMG_ROOT / relative_path.parent


def render_translations(translations, out_dir, measure_draw):
    """Genera las imagenes BMP correspondientes a las traducciones."""
    out_dir.mkdir(parents=True, exist_ok=True)

    image_count = 0

    for name, text in translations.items():
        if isinstance(text, str):
            create_bmp_with_text(
                out_dir / name,
                text,
                measure_draw,
            )
            image_count += 1

    return image_count


def process_locale_file(json_path, measure_draw):
    """Procesa un locale.json y genera sus imagenes correspondientes."""
    translations = load_locale_json(json_path)
    out_dir = get_output_directory(json_path)

    return render_translations(
        translations,
        out_dir,
        measure_draw,
    )


def main():
    start_time = time.perf_counter()

    json_files = sorted(I18N_ROOT.rglob("*.json"))

    if not json_files:
        print(f"No se encontraron archivos locale.json en: {I18N_ROOT}")
        return 1

    # Imagen auxiliar utilizada exclusivamente para medir texto.
    # Se crea una sola vez y su ImageDraw se reutiliza durante todo el proceso.
    measure_image = Image.new("RGB", (1, 1))
    measure_draw = ImageDraw.Draw(measure_image)

    image_count = 0

    try:
        for json_path in json_files:
            image_count += process_locale_file(
                json_path,
                measure_draw,
            )
    finally:
        # Liberamos el recurso auxiliar al finalizar todo el procesamiento.
        measure_image.close()

    elapsed_time = time.perf_counter() - start_time

    print("\n¡Proceso completado!")
    print(f"Imagenes creadas: {image_count}")
    print(f"Tiempo total: {elapsed_time:.2f} segundos")
    print(f"Imagenes generadas en: {IMG_ROOT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
