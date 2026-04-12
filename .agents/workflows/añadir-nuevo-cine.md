---
description: Guía detallada para añadir una nueva sala de cine al ecosistema de Cine GC
---

# Cómo añadir un nuevo Cine a la Aplicación

Sigue estos pasos para integrar una nueva sala de cine manteniendo todas las funcionalidades premium (posters, notas, géneros y sinopsis).

## 1. Modificar el Scraper (`scraper/main.py`)

Debes crear una nueva función de extracción para el cine y registrarla en el proceso principal.

### Paso A: Crear la función de scraping
Añade una función que use `cloudscraper` o `BeautifulSoup`. 
**IMPORTANTE**: Para cada película encontrada, DEBES llamar a la función `get_movie_tmdb_info(titulo_limpio)` para obtener los datos premium.

Ejemplo de estructura:
```python
def scrape_nuevo_cine():
    print("Obteniendo cartelera: Nuevo Cine...")
    url = "URL_DEL_CINE"
    results = {"Nombre del Cine": []}
    # ... lógica de extracción ...
    info = get_movie_tmdb_info(titulo_extraido)
    results["Nombre del Cine"].append({
        "title": titulo_extraido,
        "time": hora_extraida,
        "rating": info["rating"],
        "poster": info["poster"],
        "summary": info["summary"],
        "genres": info["genres"]
    })
    return results
```

### Paso B: Registrar la función en `main()`
En la función `main()`, añade tu nueva función al diccionario `all_data`:
```python
def main():
    # ...
    all_data.update(scrape_nuevo_cine())
    # ...
```

## 2. Actualizar la Interfaz (`src/App.jsx`)

Para que el botón "COMPRAR" funcione correctamente para el nuevo cine, debes añadir su enlace oficial.

1. Busca el objeto `CINEMA_LINKS`.
2. Añade la nueva entrada exacta:
```javascript
const CINEMA_LINKS = {
    // ... existentes ...
    "Nombre del Cine": "https://enlace-compra-oficial.com"
};
```

## 3. Actualizar el Selector
El selector de cines es dinámico, por lo que una vez que el scraper genere el archivo `data.js` con el nuevo nombre, aparecerá automáticamente en el desplegable de la web.

## 4. Despliegue
Una vez realizados los cambios:
1. Ejecuta `python scraper/main.py` localmente para verificar que no hay errores.
2. Sube los cambios a GitHub: `git add .`, `git commit -m "Añadido nuevo cine: Nombre"`, `git push origin main`.

---
*Nota: Gracias al sistema de caché (`tmdb_cache.json`), si las películas del nuevo cine ya existen en otras salas, no se consumirán créditos extra de la API.*
