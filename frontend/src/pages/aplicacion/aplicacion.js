import '../../../assets/main.css';
import './aplicacion.css';
import { renderPqrsSidebar } from '../../components/pqrs-sidebar/pqrs-sidebar.js';
import { renderPqrDetail } from '../../components/pqr-detail/pqr-detail.js';
import { router } from '../../app/router.js';
import { getDashboardData } from '../../service/api.js';

/* ================================================================
   APLICACION.JS — Página de gestión PQRS
   ================================================================
   Ruta: /aplicacion
   Ruta con selección: /aplicacion/RAD-2026-04821

   Layout de 3 columnas:
     [Sidebar bandeja] | [Detalle PQR] | [Panel derecho]

   Primera carga (sin ID) → muestra pantalla de bienvenida.
   Al hacer click en un item → navega a /aplicacion/:id y carga detalle.

   Nota: el widget de accesibilidad NO se renderiza en esta página.
   ================================================================ */

/**
 * Extrae el ID de PQR de la URL actual.
 * e.g. /aplicacion/RAD-2026-04821 → "RAD-2026-04821"
 *      /aplicacion                 → null
 */
function getPqrIdFromPath(path) {
    const match = path.match(/^\/aplicacion\/(.+)$/);
    return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Renderiza la pantalla de bienvenida en el área principal.
 */
async function renderWelcome(mainAreaEl) {
    // Render skeleton/loading state first
    mainAreaEl.innerHTML = `
        <div class="aplicacion-welcome">
            <div class="aplicacion-welcome__icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" x2="8" y1="13" y2="13"/>
                    <line x1="16" x2="8" y1="17" y2="17"/>
                    <line x1="10" x2="8" y1="9" y2="9"/>
                </svg>
            </div>
            <h2 class="aplicacion-welcome__title">¡Hola, bienvenido de nuevo! 👋</h2>
            <p class="aplicacion-welcome__subtitle">Cargando tus estadísticas...</p>
        </div>
    `;

    let stats = { pendientes: 0, vencen_hoy: 0, total: 0 };
    try {
        stats = await getDashboardData();
    } catch (error) {
        console.error("Error fetching dashboard stats:", error);
    }

    mainAreaEl.innerHTML = `
        <div class="aplicacion-welcome">
            <div class="aplicacion-welcome__icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" x2="8" y1="13" y2="13"/>
                    <line x1="16" x2="8" y1="17" y2="17"/>
                    <line x1="10" x2="8" y1="9" y2="9"/>
                </svg>
            </div>

            <h2 class="aplicacion-welcome__title">
                ¡Hola, bienvenido de nuevo! 👋
            </h2>

            <p class="aplicacion-welcome__subtitle">
                Tienes solicitudes pendientes esperando tu atención.
                Selecciona una PQR de la bandeja para comenzar a gestionarla.
            </p>

            <div class="aplicacion-welcome__hint">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                Haz clic en cualquier PQR del panel izquierdo
            </div>

            <div class="aplicacion-welcome__stats">
                <div class="aplicacion-welcome__stat">
                    <div class="aplicacion-welcome__stat-num">${stats.pendientes}</div>
                    <div class="aplicacion-welcome__stat-label">Pendientes</div>
                </div>
                <div class="aplicacion-welcome__stat">
                    <div class="aplicacion-welcome__stat-num">${stats.vencen_hoy}</div>
                    <div class="aplicacion-welcome__stat-label">Vence pronto</div>
                </div>
                <div class="aplicacion-welcome__stat">
                    <div class="aplicacion-welcome__stat-num">${stats.total}</div>
                    <div class="aplicacion-welcome__stat-label">Total Histórico</div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Función principal de renderizado de la página Aplicacion.
 * Llamada por el router cada vez que la ruta es /aplicacion o /aplicacion/:id
 */
export function renderAplicacion() {
    const app = document.getElementById('app');
    const currentPath = window.location.pathname;
    const activePqrId = getPqrIdFromPath(currentPath);

    // ── Shell del layout (sin navbar, sin a11y widget) ──────────
    app.innerHTML = `
        <div class="aplicacion-shell">
            <div class="aplicacion-content">

                <!-- Sidebar col -->
                <div class="aplicacion-sidebar-col" id="aplicacion-sidebar"></div>

                <!-- Área principal -->
                <div class="aplicacion-main-area" id="aplicacion-main"></div>

            </div>
        </div>
    `;

    const sidebarCol = document.getElementById('aplicacion-sidebar');
    const mainArea   = document.getElementById('aplicacion-main');

    // ── Callback cuando el usuario selecciona un PQR ─────────────
    function onSelectPqr(pqrId) {
        const newPath = `/aplicacion/${pqrId}`;
        window.history.pushState({}, '', newPath);

        // Re-renderizar sidebar con nuevo item activo
        renderPqrsSidebar(sidebarCol, {
            activeId: pqrId,
            onSelect: onSelectPqr,
        });

        // Renderizar detalle
        renderPqrDetail(mainArea, pqrId);
    }

    // ── Renderizar sidebar ────────────────────────────────────────
    renderPqrsSidebar(sidebarCol, {
        activeId: activePqrId,
        onSelect: onSelectPqr,
    });

    // ── Renderizar área principal ─────────────────────────────────
    if (activePqrId) {
        renderPqrDetail(mainArea, activePqrId);
    } else {
        renderWelcome(mainArea);
    }
}
