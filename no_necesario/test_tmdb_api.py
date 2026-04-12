import requests
import json

API_KEY = "f93979c3b2100a4a37b08d7c1228f32c"

def test_tmdb_movie(title):
    print(f"Buscando información de: {title}...")
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "es-ES"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                movie = results[0]
                rating = movie.get("vote_average")
                poster_path = movie.get("poster_path")
                full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "No poster"
                
                print("\n¡Éxito! Datos encontrados:")
                print(f"  Título oficial: {movie.get('title')}")
                print(f"  Valoración: {rating} / 10")
                print(f"  Poster: {full_poster_url}")
                print(f"  Sinopsis: {movie.get('overview')[:150]}...")
            else:
                print("No se encontraron resultados para ese título.")
        else:
            print(f"Error en la API de TMDb: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error técnico: {e}")

if __name__ == "__main__":
    test_tmdb_movie("Torrente Presidente")
    print("\n--- Otra prueba ---")
    test_tmdb_movie("Super Mario Bros. La película")
