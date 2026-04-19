import './map-view.css';
import { mapService } from '../../service/api.js';

/* ================================================================
   MAP-VIEW.JS — Componente de Mapa de Calor de Comunas
   ================================================================
   Visualiza la densidad de PQRS por comunas de Medellín.
   Usa Leaflet.js para el mapa base y marcadores de calor.
   ================================================================ */

const MEDELLIN_COORDS = [6.2476, -75.5658];

// Centroides aproximados de las 16 comunas de Medellín
const COMUNAS_CENTROIDES = {
    1:  { name: 'Popular',           coords: [6.294, -75.545] },
    2:  { name: 'Santa Cruz',        coords: [6.299, -75.556] },
    3:  { name: 'Manrique',          coords: [6.275, -75.548] },
    4:  { name: 'Aranjuez',          coords: [6.284, -75.561] },
    5:  { name: 'Castilla',          coords: [6.302, -75.576] },
    6:  { name: 'Doce de Octubre',   coords: [6.306, -75.589] },
    7:  { name: 'Robledo',           coords: [6.278, -75.594] },
    8:  { name: 'Villa Hermosa',     coords: [6.255, -75.546] },
    9:  { name: 'Buenos Aires',      coords: [6.239, -75.549] },
    10: { name: 'La Candelaria',     coords: [6.249, -75.567] },
    11: { name: 'Laureles-Estadio',  coords: [6.252, -75.592] },
    12: { name: 'La América',        coords: [6.253, -75.604] },
    13: { name: 'San Javier',        coords: [6.251, -75.618] },
    14: { name: 'El Poblado',        coords: [6.210, -75.571] },
    15: { name: 'Guayabal',          coords: [6.214, -75.587] },
    16: { name: 'Belén',             coords: [6.231, -75.599] }
};

export async function renderMapView(containerEl) {
    containerEl.innerHTML = `
        <div class="map-view">
            <header class="map-view__header">
                <div class="map-view__title">
                    <h2>Densidad de PQRS por Comunas</h2>
                    <p id="map-subtitle">Cargando datos geográficos...</p>
                </div>
            </header>
            
            <div class="map-view__container">
                <div id="medellin-map"></div>
                
                <!-- Leyenda -->
                <div class="map-view__overlay">
                    <div class="map-view__legend-title">Intensidad de PQRS</div>
                    <div class="map-view__legend-item">
                        <div class="map-view__legend-color" style="background: #ef4444;"></div> Alta (+10)
                    </div>
                    <div class="map-view__legend-item">
                        <div class="map-view__legend-color" style="background: #f97316;"></div> Media (5-10)
                    </div>
                    <div class="map-view__legend-item">
                        <div class="map-view__legend-color" style="background: #3b82f6;"></div> Baja (1-4)
                    </div>
                    <div class="map-view__legend-item">
                        <div class="map-view__legend-color" style="background: #94a3b8;"></div> Sin reportes
                    </div>
                </div>

                <!-- Panel de Información -->
                <div class="map-info-panel" id="map-info-panel">
                    <div class="map-info-panel__grid">
                        <div class="map-info-panel__left">
                            <div class="map-info-panel__header">
                                <h3 id="panel-comuna-name">Comuna</h3>
                            </div>
                            <div class="map-info-panel__count" id="panel-comuna-count">0</div>
                            <div class="map-info-panel__stat-label">Reportes totales</div>
                        </div>
                        <div class="map-info-panel__right">
                            <div class="map-info-panel__ai">
                                <div class="map-info-panel__ai-title">Análisis IA (Gemini)</div>
                                <div class="map-info-panel__ai-text" id="panel-comuna-ai">
                                    No hay suficiente información para un análisis detallado en esta zona.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inicializar Mapa
    // Esperamos un frame para que el contenedor tenga dimensiones
    requestAnimationFrame(async () => {
        const map = L.map('medellin-map', {
            center: MEDELLIN_COORDS,
            zoom: 13,
            zoomControl: false
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }).addTo(map);

        L.control.zoom({ position: 'bottomright' }).addTo(map);

        try {
            const data = await mapService.getDensity();
            document.getElementById('map-subtitle').textContent = 
                `Visualizando ${data.total_mapped} reportes geolocalizados de ${data.total_pqrs} totales.`;

            // Dibujar comunas
            data.communes.forEach(comm => {
                const config = COMUNAS_CENTROIDES[comm.id];
                if (!config) return;

                const color = comm.count > 10 ? '#ef4444' : (comm.count > 5 ? '#f97316' : '#3b82f6');
                const radius = 15 + Math.min(comm.count * 2, 30);

                const circle = L.circleMarker(config.coords, {
                    radius: radius,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.7
                }).addTo(map);

                circle.bindTooltip(config.name, {
                    permanent: false,
                    direction: 'top',
                    className: 'leaflet-tooltip-custom'
                });

                circle.on('click', () => {
                    showInfoPanel(comm);
                });
            });

        } catch (error) {
            console.error("Error loading map data:", error);
            document.getElementById('map-subtitle').textContent = "Error al cargar datos del mapa.";
        }
    });

    function showInfoPanel(comm) {
        const panel = document.getElementById('map-info-panel');
        document.getElementById('panel-comuna-name').textContent = `Comuna ${comm.id}: ${comm.name}`;
        document.getElementById('panel-comuna-count').textContent = comm.count;
        document.getElementById('panel-comuna-ai').textContent = comm.ai_summary || "Gemini no ha generado un resumen para esta comuna todavía.";
        
        panel.classList.add('active');
    }
}
