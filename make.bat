@ECHO OFF

PUSHD %~dp0

if "%1" == "" call :build
else goto :%1
POPD
EXIT /B %ERRORLEVEL%

build:
    CALL :doc
    python3 setup.py build_plugin
    EXIT /B %ERRORLEVEL%

clean:
    REM TODO
    FOR /F "delims=" %%F IN ('dir /S /P ".cache" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P ".eggs" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P "build" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P "dist" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P "doctrees" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P "doctrees" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P "__pycache__" /AD /b') DO RMDIR /S /Q "%%F"
    FOR /F "delims=" %%F IN ('dir /S /P ".egg-info" /AD /b') DO RMDIR /S /Q "%%F"

    for /r . %F IN (*.pyc) DO DEL "%F"
    for /r . %F IN (*.pyo) DO DEL "%F"
    for /r . %F IN (*~) DO DEL "%F"

    RMDIR /S /Q datacube_query\help\html
    DEL datacube_query\metadata.txt
    DEL datacube_query\LICENSE

    EXIT /B %ERRORLEVEL%


doc:
    CALL :clean
    python3 setup.py build_sphinx
    EXIT /B %ERRORLEVEL%


test:
    CALL :clean
    python3 setup.py pytest
    EXIT /B %ERRORLEVEL%
