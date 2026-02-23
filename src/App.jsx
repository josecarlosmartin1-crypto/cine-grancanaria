import React, { useState } from 'react';
import { cinemas, movieData } from './data';
import './App.css';

const CinemaSelector = ({ selected, onSelect }) => (
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

    return (
        <div className="app-container">
            <header>
                <h1>Cine GC</h1>
                <p style={{ color: '#666', fontSize: '14px' }}>Cartelera de hoy en Gran Canaria</p>
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
