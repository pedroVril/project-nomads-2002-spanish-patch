# Traducción al español del juego Project Nomads

![Project Nomads](documentation_img/project-nomands.jpg)

## Descripción

Parche de traducción al español para **Project Nomads** (2002). El proyecto contiene las traducciones de todos los diálogos del juego y un script que genera las imágenes BMP que el juego muestra en pantalla.

## Contenido

| Ruta | Descripción |
| --- | --- |
| `src/i18n/` | Textos traducidos. Fuente principal de la traducción. |
| `src/img_locale/` | Imágenes BMP generadas por el script. |
| `src/imageGenerator.py` | Script que convierte los textos en imágenes BMP. |
| `documentation_img/` | Imágenes de apoyo para la documentación. |

## Cómo funciona

Cada diálogo del juego vive en un archivo `locale.json` que asocia el nombre de la imagen con su texto:

```json
{
    "omu_c01p00_trevayne01.bmp": "¡Tú! ¿Qué has hecho?",
    "omu_c01p00_trevayne02.bmp": "¡Los Centinelas han establecido un bloqueo!"
}
```

La estructura de carpetas de `i18n` se replica de forma idéntica en `img_locale`:

```
src/i18n/es/chapter01/part00/locale.json
        └──> src/img_locale/es/chapter01/part00/omu_c01p00_trevayne01.bmp
             src/img_locale/es/chapter01/part00/omu_c01p00_trevayne02.bmp
```

## Requisitos

- Python 3.x
- Pillow

```
pip install pillow
```

## Cómo ejecutar

Desde la carpeta `src`:

```
python imageGenerator.py
```

Las imágenes generadas quedan en `src/img_locale/`.

## Cómo traducir

1. Edita los textos en los `locale.json` dentro de `src/i18n/`.
2. Ejecuta el script para regenerar las imágenes.
3. No cambies el nombre de las claves (la parte antes de `:`) ni los archivos: el juego las busca con ese nombre exacto.

Se puede usar `\n` dentro de un texto para forzar un salto de línea.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
