@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

rem ===========================================================================
rem  Instalador del parche de traduccion al espanol - Project Nomads (2002)
rem
rem  Este archivo vive DENTRO de la carpeta de imagenes (img_locale).
rem  Busca todas las carpetas chapterXX\partYY de img_locale (las que esten
rem  dentro de es/ tambien) y copia sus imagenes hacia:
rem    C:\Program Files (x86)\Project Nomads\Run\book\chapterXX\partYY\subtitle
rem
rem  USO:
rem    Doble clic en el archivo, o desde una terminal:
rem      instalar_traduccion.bat
rem    Si el juego esta en otra ruta:
rem      instalar_traduccion.bat "D:\Juegos\Project Nomads\Run\book"
rem ===========================================================================

rem --- Configuracion (edita aqui si tu ruta es distinta) ---
set "GAME_BOOK=C:\Program Files (x86)\Project Nomads\Run\book"
if not "%~1"=="" set "GAME_BOOK=%~1"

rem La carpeta de imagenes es donde vive este archivo:
set "SOURCE_DIR=%~dp0"

rem --- Elevar a administrador (Program Files exige permisos) ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   Solicitando permisos de administrador...
    echo.
    echo   Acepta el aviso de Windows que acaba de aparecer.
    echo   La instalacion continuara en una nueva ventana.
    echo.
    if "%~1"=="" (
        powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    ) else (
        powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -ArgumentList '%~1' -Verb RunAs"
    )
    echo   Si no aparecio el aviso, cierra esta ventana y ejecuta
    echo   el archivo con clic derecho -^> Ejecutar como administrador.
    echo.
    pause
    exit /b
)

rem --- Validaciones ---
dir /ad /b /s "%SOURCE_DIR%chapter*" >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encontraron carpetas chapterXX en:
    echo   %SOURCE_DIR%
    echo.
    echo Asegurate de ejecutar el archivo que esta dentro de la carpeta
    echo img_locale del proyecto descargado.
    pause
    exit /b 1
)

if not exist "!GAME_BOOK!\chapter00" (
    echo ERROR: No se encontro el juego instalado en:
    echo   !GAME_BOOK!
    echo.
    echo Opciones:
    echo   - Edita la variable GAME_BOOK al inicio de este archivo.
    echo   - Pasa la ruta como argumento:
    echo       instalar_traduccion.bat "D:\Juegos\Project Nomads\Run\book"
    pause
    exit /b 1
)

echo.
echo   Carpeta de traducciones: %SOURCE_DIR%
echo   Destino del juego:      %GAME_BOOK%
echo.

set /a COPIADOS=0
set /a ERRORES=0

for /d /r "%SOURCE_DIR%" %%C in (chapter*) do (
    for /d %%P in ("%%C\*") do (
        set "DEST=!GAME_BOOK!\%%~nC\%%~nP\subtitle"
        if not exist "!DEST!" (
            echo   [AVISO] No existe la carpeta destino: !DEST!
            set /a ERRORES+=1
        ) else (
            for %%F in ("%%P\*.bmp") do (
                copy /y "%%F" "!DEST!\" >nul 2>&1
                if errorlevel 1 (
                    set /a ERRORES+=1
                ) else (
                    set /a COPIADOS+=1
                )
            )
            echo   [%%~nC\%%~nP] copiados: !COPIADOS! archivos
        )
    )
)

echo.
echo ============================ RESUMEN ============================
echo   Archivos copiados: %COPIADOS%
echo   Errores:           %ERRORES%
echo =================================================================
echo.
if %ERRORES% equ 0 (
    echo   Instalacion completada correctamente.
    echo   Inicia el juego y verifica las nuevas imagenes.
) else (
    echo   Hubo errores. Revisa los mensajes anteriores.
)
echo.
pause
