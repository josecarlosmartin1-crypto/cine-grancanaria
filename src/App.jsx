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

const Modal = ({ movie, onClose }) => {
    if (!movie) return null;
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="close-button" onClick={onClose}>&times;</button>
                <div className="modal-header-info">
                    <img src={movie.poster} alt={movie.title} className="modal-poster" />
                    <div className="modal-text-header">
                        <h2>{movie.title}</h2>
                        <div className="modal-meta">
                            <span className="modal-time">{movie.time}</span>
                            <span className="modal-rating">⭐ {movie.rating}</span>
                        </div>
                    </div>
                </div>
                <div className="modal-body">
                    <h3>Sinopsis</h3>
                    <p>{movie.summary}</p>
                </div>
            </div>
        </div>
    );
};

const MovieCard = ({ movie, onShowSummary }) => {
    const getRatingColor = (rating) => {
        if (rating >= 7.5) return '#4caf50';
        if (rating >= 5.5) return '#ffc107';
        if (rating > 0) return '#ff5722';
        return '#888';
    };

    return (
        <div className="movie-card">
            <div className="movie-card-inner">
                {movie.poster ? (
                    <div className="movie-poster-container">
                        <img src={movie.poster} alt={movie.title} className="movie-poster" loading="lazy" />
                    </div>
                ) : (
                    <div className="movie-poster-placeholder">🍿</div>
                )}
                
                <div className="movie-details">
                    <div className="movie-header">
                        <span className="movie-time">{movie.time}</span>
                        <div 
                            className="movie-rating-badge" 
                            style={{ backgroundColor: getRatingColor(movie.rating) }}
                        >
                            {movie.rating > 0 ? movie.rating : 'N/A'}
                        </div>
                    </div>
                    <h2 className="movie-title">{movie.title}</h2>
                    <div className="movie-summary-tap" onClick={() => onShowSummary(movie)}>
                        <p className="movie-summary">{movie.summary || "Ver detalles en web."}</p>
                        <span className="tap-hint">Pulsa para leer más</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

function App() {
    const [selectedCinema, setSelectedCinema] = useState("Artesiete Las Terrazas");
    const [selectedMovieForSummary, setSelectedMovieForSummary] = useState(null);

    const movies = movieData[selectedCinema] || [];
    const sortedMovies = [...movies].sort((a, b) => a.time.localeCompare(b.time));

    const today = new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    const formattedDate = today.charAt(0).toUpperCase() + today.slice(1);

    return (
        <div className="app-container">
            <header>
                <h1>Cine GC</h1>
                <p style={{ color: '#666', fontSize: '14px' }}>Cartelera del {formattedDate}</p>
                <p style={{ color: '#999', fontSize: '11px', marginTop: '4px' }}>Notas y Sinopsis por TMDb</p>
            </header>

            <CinemaSelector selected={selectedCinema} onSelect={setSelectedCinema} />

            <div className="movie-list">
                {sortedMovies.length > 0 ? (
                    sortedMovies.map((movie, index) => (
                        <MovieCard 
                            key={index} 
                            movie={movie} 
                            onShowSummary={setSelectedMovieForSummary} 
                        />
                    ))
                ) : (
                    <div className="empty-state">No hay películas programadas para hoy.</div>
                )}
            </div>

            <Modal 
                movie={selectedMovieForSummary} 
                onClose={() => setSelectedMovieForSummary(null)} 
            />
        </div>
    );
}

export default App;
