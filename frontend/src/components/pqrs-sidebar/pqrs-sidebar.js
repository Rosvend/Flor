import './pqrs-sidebar.css';
import { getActivePqrs, getDashboardData } from '../../service/api.js';
import { router } from '../../app/router.js';

/* ================================================================
   PQRS-SIDEBAR.JS — Componente de bandeja lateral
   ================================================================
   Renderiza el panel izquierdo con la lista de PQRs pendientes.
   Se resalta el item activo según el ID en la ruta actual.

   API del componente:
     renderPqrsSidebar(containerEl, options)
     options.activeId  — ID del PQR actualmente seleccionado
     options.onSelect  — callback(pqrId) cuando se hace click
   ================================================================ */

/**
 * Calcula el texto y clase del badge de vencimiento.
 * @param {string} fechaVence — ISO date string
 */
function getVenceBadge(fechaVence) {
    if (!fechaVence) return { text: 'Sin fecha', cls: 'pqrs-vence-badge--normal' };
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const vence = new Date(fechaVence);
    vence.setHours(0, 0, 0, 0);
    const diff = Math.round((vence - hoy) / (1000 * 60 * 60 * 24));

    if (diff <= 0) return { text: 'Vence Hoy', cls: 'pqrs-vence-badge--hoy' };
    if (diff <= 3)  return { text: `Vence ${diff} día${diff > 1 ? 's' : ''}`, cls: 'pqrs-vence-badge--pronto' };
    return { text: `Vence ${diff} días`, cls: 'pqrs-vence-badge--normal' };
}

/**
 * Devuelve la clase del badge de tipo.
 */
function getTipoBadgeClass(tipo) {
    const map = {
        PETICION:   'pqrs-tipo-badge--peticion',
        QUEJA:      'pqrs-tipo-badge--queja',
        RECLAMO:    'pqrs-tipo-badge--reclamo',
        SUGERENCIA: 'pqrs-tipo-badge--sugerencia',
    };
    return map[tipo?.toUpperCase()] || 'pqrs-tipo-badge--peticion';
}

/**
 * Renderiza el HTML de un item de la lista.
 */
function renderItem(pqr, isActive) {
    // Calculamos fecha de vencimiento estimada (+15 días si no existe)
    const fechaRadicado = pqr.timestamp_radicacion || new Date().toISOString();
    const d = new Date(fechaRadicado);
    d.setDate(d.getDate() + 15);
    const fechaVence = d.toISOString();

    const vence = getVenceBadge(fechaVence);
    const tipoClass = getTipoBadgeClass(pqr.tipo);
    const activeClass = isActive ? 'pqrs-item--active' : '';
    const pqrTipo = pqr.tipo || 'Peticion';
    const tipoLabel = pqrTipo.charAt(0).toUpperCase() + pqrTipo.slice(1).toLowerCase();
    
    // Asunto: Usamos el texto mejorado de IA o los primeros 60 caracteres del contenido
    const contenidoStr = pqr.contenido || 'Sin contenido detallado';
    const asunto = pqr.analisis_ia?.texto_mejorado || contenidoStr.substring(0, 60) + '...';
    const confianza = pqr.analisis_ia ? 99 : 0; // Placeholder confianza

    return `
        <div
            class="pqrs-item ${activeClass}"
            data-pqr-id="${pqr.radicado}"
            role="button"
            tabindex="0"
            aria-label="PQR ${pqr.radicado}: ${asunto}"
            aria-pressed="${isActive}"
        >
            <div class="pqrs-item__top">
                <span class="pqrs-item__id">${pqr.radicado}</span>
                <span class="pqrs-vence-badge ${vence.cls}">${vence.text}</span>
            </div>
            <p class="pqrs-item__asunto">${asunto}</p>
            <div class="pqrs-item__bottom">
                <span class="pqrs-tipo-badge ${tipoClass}">${tipoLabel}</span>
                <span class="pqrs-conf-badge">${confianza}% Conf.</span>
            </div>
        </div>
    `;
}

/**
 * Renderiza la sidebar completa dentro de `containerEl`.
 *
 * @param {HTMLElement} containerEl — El elemento donde se monta el sidebar
 * @param {{ activeId?: string, onSelect?: Function }} options
 */
export async function renderPqrsSidebar(containerEl, options = {}) {
    const { activeId = null, onSelect = () => {} } = options;

    // Estado de carga
    containerEl.innerHTML = `
        <aside class="pqrs-sidebar" aria-label="Bandeja de PQRs">
            <div class="pqrs-sidebar__brand">
                <div class="pqrs-sidebar__brand-icon">G</div>
                <div class="pqrs-sidebar__brand-text">
                    <h2>Gestión PQRS</h2>
                    <p>Playground Administrativo</p>
                </div>
            </div>
            <div class="pqrs-sidebar__bandeja-header">Cargando...</div>
        </aside>
    `;

    let items = [];
    let stats = { pendientes: 0 };
    try {
        [items, stats] = await Promise.all([
            getActivePqrs(),
            getDashboardData()
        ]);
    } catch (e) {
        console.error(e);
        containerEl.innerHTML = `<div class="pqrs-sidebar"><p style="padding:1rem;color:red;">Error cargando bandeja</p></div>`;
        return;
    }

    const itemsHTML = items.map(pqr => renderItem(pqr, pqr.radicado === activeId)).join('');

    containerEl.innerHTML = `
        <aside class="pqrs-sidebar" aria-label="Bandeja de PQRs">

            <!-- Brand -->
            <div class="pqrs-sidebar__brand">
                <div class="pqrs-sidebar__brand-icon">G</div>
                <div class="pqrs-sidebar__brand-text">
                    <h2>Gestión PQRS</h2>
                    <p>Playground Administrativo</p>
                </div>
            </div>

            <!-- Bandeja header -->
            <div class="pqrs-sidebar__bandeja-header">
                Bandeja PQRS (${stats.pendientes} pendientes)
            </div>

            <!-- Lista -->
            <div class="pqrs-sidebar__list" role="list" aria-label="Lista de PQRs pendientes">
                ${itemsHTML}
            </div>

            <!-- Footer -->
            <div class="pqrs-sidebar__footer">
                <button class="pqrs-sidebar__footer-btn" id="sidebar-btn-estadisticas">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                    Estadísticas
                </button>
                <button class="pqrs-sidebar__footer-btn" id="sidebar-btn-configuracion">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
                    Configuración
                </button>
            </div>
        </aside>
    `;

    // ── Event listeners ──────────────────────────────────────────
    const list = containerEl.querySelector('.pqrs-sidebar__list');

    list.addEventListener('click', (e) => {
        const item = e.target.closest('[data-pqr-id]');
        if (!item) return;
        const id = item.dataset.pqrId;
        onSelect(id);
    });

    list.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            const item = e.target.closest('[data-pqr-id]');
            if (item) {
                e.preventDefault();
                const id = item.dataset.pqrId;
                onSelect(id);
            }
        }
    });

    // ── Footer buttons listeners ──────────────────────────────────
    const btnStats = containerEl.querySelector('#sidebar-btn-estadisticas');
    const btnConfig = containerEl.querySelector('#sidebar-btn-configuracion');

    btnStats?.addEventListener('click', () => {
        onSelect('estadisticas');
    });

    btnConfig?.addEventListener('click', () => {
        onSelect('configuracion');
    });
}
