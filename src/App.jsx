import React, { useState, useEffect, useRef } from 'react';
import { cinemas as defaultCinemas, movieData as defaultMovieData, LAST_UPDATED } from './data';
import './App.css';

const CACHE_KEY = 'cine_gc_live_cache_v1';

function getCanaryTodayIso() {
    const parts = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Atlantic/Canary',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).formatToParts(new Date());
    const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
    return `${map.year}-${map.month}-${map.day}`;
}

function formatDateEs(isoDate) {
    if (!isoDate) return '';
    const [year, month, day] = isoDate.split('-').map(Number);
    const dateObj = new Date(Date.UTC(year, month - 1, day, 12, 0, 0));
    const formatted = dateObj.toLocaleDateString('es-ES', {
        timeZone: 'Atlantic/Canary',
        weekday: 'long',
        day: 'numeric',
        month: 'long'
    });
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

const CINEMA_LINKS = {
    "Cine Yelmo Premium Alisios": "https://yelmocines.es/cartelera/las-palmas/premium-alisios",
    "Cine Yelmo Las Arenas": "https://yelmocines.es/cartelera/las-palmas/las-arenas",
    "Cine Yelmo Vecindario": "https://yelmocines.es/cartelera/las-palmas/vecindario",
    "Ocine Premium Siete Palmas": "https://www.ocinepremium7palmas.es/",
    "Artesiete Las Terrazas": "https://terrazas.artesiete.es/Cine/1/ARTESIETE%20Las%20Terrazas/Total"
};

const CinemaSelector = ({ selected, onSelect, cinemas }) => (
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

const GenrePills = ({ genres }) => {
    if (!genres || genres.length === 0) return null;
    return (
        <div className="genre-pills">
            {genres.map((genre, idx) => (
                <span key={idx} className="genre-pill">{genre}</span>
            ))}
        </div>
    );
};

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
                        <GenrePills genres={movie.genres} />
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
        <div className="movie-card" onClick={() => onShowSummary(movie)}>
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
                    
                    <GenrePills genres={movie.genres} />

                    <div className="movie-summary-tap">
                        <p className="movie-summary">{movie.summary || "Ver detalles en web."}</p>
                        <span className="tap-hint">Pulsa para leer más</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

function App() {
    const todayIso = getCanaryTodayIso();
    const [selectedCinema, setSelectedCinema] = useState("Artesiete Las Terrazas");
    const [selectedMovieForSummary, setSelectedMovieForSummary] = useState(null);
    const [liveData, setLiveData] = useState(() => {
        try {
            const raw = localStorage.getItem(CACHE_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (parsed?.updatedAt === todayIso && parsed?.movieData) {
                    return parsed;
                }
            }
        } catch {
            // Ignorar errores de localStorage
        }
        return null;
    });
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [refreshError, setRefreshError] = useState("");

    useEffect(() => {
        if (liveData) {
            try {
                localStorage.setItem(CACHE_KEY, JSON.stringify(liveData));
            } catch {
                // Ignorar si el almacenamiento está lleno
            }
        }
    }, [liveData]);

    const activeMovieData = liveData?.movieData || defaultMovieData;
    const activeCinemas = Object.keys(activeMovieData).length > 0 ? Object.keys(activeMovieData) : defaultCinemas;
    const activeDateIso = liveData?.updatedAt || LAST_UPDATED || todayIso;
    const isOutdated = activeDateIso < todayIso;
    const autoRefreshedRef = useRef(false);

    const handleRefresh = async () => {
        if (isRefreshing) return;
        setIsRefreshing(true);
        setRefreshError("");
        try {
            const res = await fetch('/api/refresh');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const payload = await res.json();
            if (!payload?.movieData) throw new Error("Respuesta inválida");

            // Conservamos los datos previos de un cine si la captura en vivo devolvió vacío
            const merged = { ...activeMovieData };
            for (const [cinema, sessions] of Object.entries(payload.movieData)) {
                if (Array.isArray(sessions) && sessions.length > 0) {
                    merged[cinema] = sessions;
                }
            }
            setLiveData({
                updatedAt: payload.updatedAt || todayIso,
                movieData: merged
            });
        } catch {
            setRefreshError("No se pudo actualizar ahora.");
        } finally {
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        if (isOutdated && !autoRefreshedRef.current) {
            autoRefreshedRef.current = true;
            handleRefresh();
        }
    }, [isOutdated]);

    const movies = activeMovieData[selectedCinema] || [];
    const sortedMovies = [...movies].sort((a, b) => a.time.localeCompare(b.time));
    const formattedDate = formatDateEs(activeDateIso);

    return (
        <div className="app-container">
            <header>
                <h1>Cine GC</h1>
                <div className="date-refresh-row">
                    <p className="date-label">
                        Cartelera del {formattedDate}
                        {isOutdated && <span className="outdated-badge">Desactualizada</span>}
                    </p>
                    <button
                        type="button"
                        className="refresh-button"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        title="Actualizar cartelera ahora"
                    >
                        <span className={isRefreshing ? "spin" : ""}>↻</span>
                        {isRefreshing ? " Actualizando..." : " Actualizar"}
                    </button>
                </div>
                {refreshError && <p className="refresh-error">{refreshError}</p>}
                <p style={{ color: '#999', fontSize: '11px', marginTop: '4px' }}>Notas, Géneros y Sinopsis por TMDb</p>
            </header>

            <CinemaSelector selected={selectedCinema} onSelect={setSelectedCinema} cinemas={activeCinemas} />

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
