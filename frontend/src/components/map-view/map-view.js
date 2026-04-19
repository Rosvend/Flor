import './map-view.css';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { request } from '../../service/api.js';

export async function renderMapView(container) {
    container.innerHTML = `
        <div class="map-view">
            <div class="map-view__header">
                <div>
                    <h2 class="map-view__title">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" x2="9" y1="3" y2="18"></line><line x1="15" x2="15" y1="6" y2="21"></line></svg>
                        Mapa de Densidad (Comunas)
                    </h2>
                    <p class="map-view__subtitle">Análisis geográfico y causal generado por Inteligencia Artificial</p>
                </div>
            </div>
            <div class="map-view__container">
                <div class="map-view__loading" id="map-loading">
                    <div class="map-view__spinner"></div>
                    <p>IA analizando ubicación y causas de PQRS...</p>
                </div>
                <div id="leaflet-map"></div>
            </div>
        </div>
    `;

    // Wait for the DOM to settle so Leaflet can get the container size
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
        // Inicializar mapa centrado en Medellín
        const map = L.map('leaflet-map').setView([6.2518, -75.5636], 12);
        
        // Agregar capa de OpenStreetMap (estilo claro/moderno)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        // Fetch data from backend
        const mapData = await request('/pqrs/dashboard/map', { method: 'GET', requiresAuth: true });

        document.getElementById('map-loading').style.display = 'none';

        if (!mapData || mapData.length === 0) {
            alert('No hay suficientes datos de ubicación para generar el mapa.');
            return;
        }

        // Determinar max count para escalar los círculos
        const maxCount = Math.max(...mapData.map(d => d.count), 1);

        // Render markers
        mapData.forEach(comuna => {
            if (comuna.count === 0) return;

            // Radio base + proporcional al max (entre 10 y 40 pixels)
            const radius = 10 + (comuna.count / maxCount) * 30;

            const circle = L.circleMarker([comuna.lat, comuna.lng], {
                radius: radius,
                fillColor: "var(--color-primary)",
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.7
            }).addTo(map);

            const popupContent = `
                <div class="comuna-popup">
                    <h3>${comuna.comuna_id} - ${comuna.nombre}</h3>
                    <div class="density-badge">${comuna.count} PQRS activas</div>
                    <p class="insight">
                        <strong>Insight IA:</strong><br/>
                        ${comuna.explicacion}
                    </p>
                </div>
            `;

            circle.bindPopup(popupContent);
            
            // Opcional: mostrar tooltip al hacer hover
            circle.bindTooltip(`Comuna ${comuna.comuna_id}: ${comuna.count} PQRS`, {
                permanent: false,
                direction: 'top'
            });
        });

    } catch (error) {
        console.error("Error cargando mapa:", error);
        document.getElementById('map-loading').innerHTML = `
            <p style="color: var(--color-danger);">Error al cargar los datos del mapa.</p>
            <p style="font-size: 0.8rem;">${error.message}</p>
        `;
    }
}
