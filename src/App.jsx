import React, { useState } from 'react';
import { cinemas, movieData } from './data';
import './App.css';

const CINEMA_LINKS = {
    "Cine Yelmo Premium Alisios": "https://yelmocines.es/cartelera/las-palmas/premium-alisios",
    "Cine Yelmo Las Arenas": "https://yelmocines.es/cartelera/las-palmas/las-arenas",
    "Cine Yelmo Vecindario": "https://yelmocines.es/cartelera/las-palmas/vecindario",
    "Ocine Premium Siete Palmas": "https://www.ocinepremium7palmas.es/",
    "Artesiete Las Terrazas": "https://terrazas.artesiete.es/Cine/1/ARTESIETE%20Las%20Terrazas/Total"
};

const CinemaSelector = ({ selected, onSelect }) => (
    <div className="cinema-header-sticky">
        <div className="cinema-select-container">
            <select
                className="cinema-select"
                value={selected}
                onChange={(e) => onSelect(e.target.value)}
            >
                {cinemas.map((cinema) => (
                    <option key={cinema} value={cinema}>
                        {cinema}
                    </option>
                ))}
            </select>
        </div>
        <a href={CINEMA_LINKS[selected]} target="_blank" rel="noopener noreferrer" className="buy-button">
            Comprar
        </a>
    </div>
);

const MovieCard = ({ movie }) => (
    <div className="movie-card">
        <div className="movie-header">
            <span className="movie-time">{movie.time}</span>
            <div className="movie-rating">
                <span>★</span>
                <span>{movie.rating}</span>
            </div>
        </div>
        <h2 className="movie-title">{movie.title}</h2>
        <p className="movie-summary">{movie.summary}</p>
    </div>
);

function App() {
    const [selectedCinema, setSelectedCinema] = useState(cinemas[0]);

    const movies = movieData[selectedCinema] || [];

    // Sort movies by time (HH:MM format)
    const sortedMovies = [...movies].sort((a, b) => a.time.localeCompare(b.time));

    const today = new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    const formattedDate = today.charAt(0).toUpperCase() + today.slice(1);

    return (
        <div className="app-container">
            <header>
                <h1>Cine GC</h1>
                <p style={{ color: '#666', fontSize: '14px' }}>Cartelera del {formattedDate}</p>
            </header>

            <CinemaSelector
                selected={selectedCinema}
                onSelect={setSelectedCinema}
            />

            <div className="movie-list">
                {sortedMovies.length > 0 ? (
                    sortedMovies.map((movie, index) => (
                        <MovieCard key={index} movie={movie} />
                    ))
                ) : (
                    <div className="empty-state">No hay películas programadas para hoy.</div>
                )}
            </div>
        </div>
    );
}

export default App;
