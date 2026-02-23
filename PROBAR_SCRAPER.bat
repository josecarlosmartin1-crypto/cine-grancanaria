@echo off
echo Instalando dependencias necesarias...
python -m pip install requests beautifulsoup4

echo Ejecutando el scraper...
python scraper/main.py

echo.
echo Proceso terminado. Ya puedes abrir PRUEBA_RAPIDA.html para ver los datos.
pause
