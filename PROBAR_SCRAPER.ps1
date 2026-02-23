# Script para probar el scraper de cine localmente
Write-Host "Instalando dependencias necesarias (requests y beautifulsoup4)..." -ForegroundColor Cyan
pip install requests beautifulsoup4

Write-Host "Ejecutando el scraper..." -ForegroundColor Cyan
python scraper/main.py

Write-Host "`n¡Proceso terminado! Ya puedes abrir el archivo PRUEBA_RAPIDA.html para ver los datos actualizados." -ForegroundColor Green
pause
