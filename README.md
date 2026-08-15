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

- Python 3.10 o superior

## Puesta en marcha (una sola vez)

El proyecto usa un **entorno virtual** para aislar las dependencias y no depender de lo que tenga instalado tu sistema.

**Importante:** para que los paquetes queden DENTRO del `.venv` y no en tu Python global, debes usar el Python del entorno virtual. Los comandos de abajo ya lo hacen, así que no es necesario "activar" nada.

1. Crea el entorno virtual (desde la raíz del proyecto):

   ```
   python -m venv .venv
   ```

2. Instala las dependencias declaradas en `pyproject.toml` usando el pip del entorno:

   - **Windows / PowerShell**:
     ```
     .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
     ```
   - **Windows / Git Bash (MINGW64)** — usa barras normales `/`, no `\`:
     ```
     .venv/Scripts/python.exe -m pip install -e ".[dev]"
     ```
   - **Linux/macOS**:
     ```
     .venv/bin/python -m pip install -e ".[dev]"
     ```

   - `.[dev]` instala `pillow` (dependencia de ejecución) y `ruff` (dependencia de desarrollo).

> **Alternativa (activando el entorno):** `.\.venv\Scripts\Activate.ps1` y luego `pip install -e ".[dev]"`. Pero si escribes `pip install` **sin haber activado**, se instala en tu Python global.

## Cómo ejecutar

Sin activar nada, desde la raíz del proyecto:

- **Windows / PowerShell**: `.\.venv\Scripts\python.exe src\imageGenerator.py`
- **Windows / Git Bash (MINGW64)**: `.venv/Scripts/python.exe src/imageGenerator.py`
- **Linux/macOS**: `.venv/bin/python src/imageGenerator.py`

O con el entorno activado:

```
image-generator
```

Las imágenes generadas quedan en `src/img_locale/`.

## Solución de problemas

### "WARNING: The script image-generator.exe is installed in '...pythoncore-3.14-64\Scripts'"

Ese warning significa que instalaste con tu pip global (no con el del `.venv`). Solución: desinstala del entorno global y vuelve a instalar con el Python del venv:

```
python -m pip uninstall -y project-nomads-spanish-patch
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Verifica dónde quedó cada cosa:

```
python -m pip list                    # entorno global (solo debe salir pip)
.\.venv\Scripts\python.exe -m pip list   # entorno virtual (pillow, ruff, el proyecto)
```

## Cómo traducir

1. Edita los textos en los `locale.json` dentro de `src/i18n/`.
2. Ejecuta el script para regenerar las imágenes.
3. No cambies el nombre de las claves (la parte antes de `:`) ni los archivos: el juego las busca con ese nombre exacto.

Se puede usar `\n` dentro de un texto para forzar un salto de línea.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
