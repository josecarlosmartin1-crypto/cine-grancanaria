# Protocolo de Mantenimiento de Scrapers (Cine Gran Canaria)

Este documento detalla las reglas de oro y las soluciones técnicas implementadas para garantizar que la captura de datos sea robusta, especialmente durante el cambio de día (medianoche y 8:00 AM).

## 1. Reglas de Gestión de Fechas (Sincronización Total)

Para evitar que los cines muestren datos del día anterior o listas vacías durante las primeras horas de la mañana, TODOS los scrapers deben ignorar la "fecha por defecto" de las webs de los cines y forzar la fecha actual del sistema (`datetime.date.today()`).

### A. Artesiete Las Terrazas
- **Lógica**: La web usa IDs rotativos para las pestañas de los días. 
- **Solución**: Se busca el elemento `<a>` cuyo atributo `mostrar` contiene el texto de la fecha de hoy (formato `dd/mm`). Del ID de ese elemento se extrae el contenedor correcto.
- **Punto Crítico**: Nunca usar `id="0"` fijo, ya que solo funciona los domingos/lunes.

### B. Yelmo Cines (Vecindario, Alisios, Las Arenas)
- **Lógica**: La API devuelve un array de objetos `Dates`. El primero (`index 0`) suele ser el día anterior hasta que el cine "rota" su sistema (aprox. 3:00 AM).
- **Solución**: El scraper busca en el array `Dates` el objeto cuyo campo `ShowtimeDate` coincida con hoy (formato `D mes`, ej: "14 abril").
- **Fallback**: Si no encuentra la fecha exacta, usa el primero de la lista.

### C. Ocine Siete Palmas
- **Lógica**: El encabezado de su API (`date`) puede estar desfasado hasta bien entrada la mañana.
- **Solución**: El script itera por todas las sesiones en `Planificacions` y solo captura aquellas cuyo campo `plan_data` coincida con la fecha real de hoy (`YYYY-MM-DD`), ignorando el `api_date` principal si está desincronizado.

## 2. Enriquecimiento de Datos (TMDb)

### Caché Persistente (`scraper/tmdb_cache.json`)
Para evitar exceder los límites de la API de TMDb y acelerar el proceso, se mantiene un historial de películas:
- Si una película ya ha sido buscada antes, se recupera su poster, nota y resumen del JSON.
- Las nuevas películas se añaden automáticamente a la memoria al finalizar el scraping.

### Limpieza de Títulos
Antes de buscar en TMDb, el script limpia los títulos de coletillas como "(Atmos)", "(Vose)" o "¡!".

## 3. Despliegue y Automatización
- El scraper se ejecuta automáticamente vía **GitHub Actions** cada día a las **08:00 UTC**.
- Los datos se guardan en `src/data.js`, el cual es importado directamente por la App en React/Vite.

---
> [!NOTE]
> Si algún cine cambia su estructura web, empezar siempre revisando los scripts de depuración en `scratch/` para identificar nuevos selectores CSS o estructuras JSON.
