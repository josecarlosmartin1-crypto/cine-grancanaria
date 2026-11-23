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
- **Solución**: El scraper busca en el array `Dates` el objeto cuyo campo `ShowtimeDate` coincida con hoy (aceptando tanto `DD mes` con cero inicial, ej. `"01 diciembre"`, como `D mes`).
- **Punto Crítico (Sesión previa)**: `https://www.yelmocines.es/now-playing.aspx/GetNowPlaying` sin cookies de sesión devuelve `403 Forbidden`. Es obligatorio hacer un `GET` previo a `https://yelmocines.es/cartelera/las-palmas/las-arenas` y enviar el `POST` a `https://yelmocines.es/now-playing.aspx/GetNowPlaying` con `Origin` y `Referer`.
- **Fallback**: Si no encuentra la fecha exacta, usa el primero de la lista.

### C. Ocine Siete Palmas
- **Lógica**: La web principal (`https://ocinepremium7palmas.es/`) migró a una SPA que embebe un iframe de `https://tickets.ocinepremium7palmas.es/` (el antiguo `/components/com_cines/json/es_cartellera.json` devuelve HTML).
- **Solución**:
    - Se llama a `POST https://tickets.ocinepremium7palmas.es/api/v1/init` para obtener el `token`.
    - Se consulta `POST https://tickets.ocinepremium7palmas.es/api/v1/sessions` para listar `pelicules`.
    - Para cada película se consulta `GET https://tickets.ocinepremium7palmas.es/api/v1/pelicula/{id}?lang=es` leyendo tanto `sessions` como `subPelicules[*].sessions`.
    - **Smart Fallback**: Busca la fecha real de hoy (`YYYY-MM-DD`) o la primera fecha futura disponible (`>= hoy`). Si falla la captura, `main.py` conserva los datos previos en `src/data.js`.

## 2. Enriquecimiento de Datos (TMDb)

### Caché Persistente (`scraper/tmdb_cache.json`)
Para evitar exceder los límites de la API de TMDb y acelerar el proceso, se mantiene un historial de películas:
- Si una película ya ha sido buscada antes, se recupera su poster, nota y resumen del JSON.
- Las nuevas películas se añaden automáticamente a la memoria al finalizar el scraping.

### Limpieza de Títulos
Antes de buscar en TMDb, el script limpia los títulos de coletillas como "(Atmos)", "(Vose)" o "¡!".

## 3. Despliegue, Automatización y Refresco en Vivo
- El scraper se ejecuta automáticamente vía **GitHub Actions** cada día a las **09:23 UTC** (con reintentos de Ocine a las **10:23** y **11:23 UTC**, evitando el minuto `:00` por saturación de colas).
- Los datos se guardan en `src/data.js` (junto con `LAST_UPDATED`), el cual es importado por la App en React/Vite.
- Si el cron de GitHub Actions falla o se retrasa, el usuario puede pulsar el botón **↻ Actualizar** en la cabecera de la web, que llama a la Serverless Function `api/refresh.js` (`/api/refresh` en Vercel, excluida de rewrites en `vercel.json`) y guarda la cartelera fresca del día en `localStorage`.

---
> [!NOTE]
> Si algún cine cambia su estructura web, empezar siempre revisando los scripts de depuración en `scratch/` para identificar nuevos selectores CSS o estructuras JSON.
