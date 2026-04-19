import './pqr-detail.css';
import { getPqrDetails, pqrsListService } from '../../service/api.js';
import { TIPO_PQRS } from '../../service/pqrs-mock.js';

/* ================================================================
   PQR-DETAIL.JS — Componente de detalle de una PQR
   ================================================================
   Renderiza el panel central + panel derecho del detalle de una PQR.
   Recibe el ID del PQR, carga datos del mock y dibuja todo.

   API:
     renderPqrDetail(containerEl, pqrId)
     containerEl — el elemento donde se monta el componente
     pqrId       — string e.g. "RAD-2026-04821"
   ================================================================ */

/* ── Helpers ────────────────────────────────────────────────────── */

function formatFecha(iso) {
    if (!iso) return 'N/A';
    const d = new Date(iso);
    const meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
    return `${d.getDate()} ${meses[d.getMonth()]} ${d.getFullYear()}`;
}

function getVenceLabel(fechaRadicado) {
    if (!fechaRadicado) return 'Sin fecha';
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const vence = new Date(fechaRadicado);
    vence.setDate(vence.getDate() + 15);
    vence.setHours(0, 0, 0, 0);
    const diff = Math.round((vence - hoy) / (1000 * 60 * 60 * 24));
    if (diff <= 0) return 'Vence Hoy';
    return `Vence en ${diff} día${diff !== 1 ? 's' : ''}`;
}

function getTipoLabel(tipo) {
    return TIPO_PQRS[tipo?.toUpperCase()]?.label || tipo;
}

/* ── Renderizado del HTML ────────────────────────────────────────── */

function buildDetailHTML(pqr) {
    const fechaRadicado = pqr.timestamp_radicacion || new Date().toISOString();
    const venceLabel = getVenceLabel(fechaRadicado);
    const tipoLabel = getTipoLabel(pqr.tipo);
    const canalLabel = pqr.canal === 'WEB' ? 'Canal Web'
        : pqr.canal === 'PRESENCIAL' ? 'Presencial'
        : pqr.canal === 'APP' ? 'App Móvil'
        : 'Facebook/Meta';

    const analisis = pqr.analisis_ia || {};
    
    // Mapeo de capas
    const capas = {
        solicitudConcreta: analisis.texto_mejorado || 'Pendiente de análisis...',
        tematicas: analisis.tipo_sugerido ? [analisis.tipo_sugerido, analisis.secretaria_asignada] : ['General'],
        textoOriginal: pqr.contenido
    };

    const tematicasHTML = capas.tematicas
        .filter(t => t)
        .map(t => `<span class="pqr-tematica-tag">${t}</span>`)
        .join('');

    // Precedente y Ciudadano (Mocks para el MVP si no hay en el backend)
    const precedente = pqr.precedente || {
        id: 'RAD-AUTO-001',
        resumen: 'Respuesta sugerida basada en casos similares de ' + (analisis.secretaria_asignada || 'Gestión General'),
        similitud: 85
    };

    const ciudadano = pqr.infoCiudadano || {
        historialLimpio: true,
        solicitudesPrevias: 0
    };

    const ciudadanoMsg = ciudadano.historialLimpio
        ? 'El ciudadano tiene historial limpio en solicitudes previas.'
        : `El ciudadano tiene ${ciudadano.solicitudesPrevias} solicitudes previas registradas.`;

    return `
        <!-- ── Panel central: detalle ── -->
        <section class="pqr-detail" aria-label="Detalle de PQR ${pqr.radicado}">

            <!-- Header -->
            <div class="pqr-detail__header">
                <div class="pqr-detail__header-left">
                    <span class="pqr-detail__tipo-tag">${tipoLabel.toUpperCase()}</span>
                    <h1 class="pqr-detail__radicado">${pqr.radicado}</h1>
                </div>
                <div class="pqr-detail__header-actions">
                    <button class="btn--reclasificar" id="btn-reclasificar" aria-label="Reclasificar esta PQR">
                        Reclasificar
                    </button>
                    <button class="btn--confirmar" id="btn-confirmar" aria-label="Confirmar clasificación">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                        Confirmar clasificación
                    </button>
                </div>
            </div>

            <!-- Meta -->
            <div class="pqr-detail__meta">
                <span class="pqr-detail__meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                    ${formatFecha(fechaRadicado)}
                </span>
                <span class="pqr-detail__meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                    ${canalLabel}
                </span>
                <span class="pqr-detail__vence-hoy">
                    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><circle cx="12" cy="12" r="10"/></svg>
                    ${venceLabel}
                </span>
            </div>

            <!-- Body (capas de análisis) -->
            <div class="pqr-detail__body">

                <!-- Capa 1: Solicitud concreta -->
                <div class="pqr-capa-card">
                    <div class="pqr-capa-card__label">
                        <span class="pqr-capa-card__label-num">1</span>
                        Capa 1 — Solicitud Concreta (IA)
                    </div>
                    <p class="pqr-capa-card__texto">${capas.solicitudConcreta}</p>
                </div>

                <!-- Capa 2: Discriminación temática -->
                <div class="pqr-capa-card">
                    <div class="pqr-capa-card__label">
                        <span class="pqr-capa-card__label-num">2</span>
                        Capa 2 — Discriminación Temática (IA)
                    </div>
                    <div class="pqr-tematicas" id="tematicas-container">
                        ${tematicasHTML}
                        <button class="pqr-tematica-add" id="btn-add-tematica" aria-label="Añadir temática">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                            Añadir
                        </button>
                    </div>
                </div>

                <!-- Capa 3: Texto original -->
                <div class="pqr-capa-card">
                    <div class="pqr-capa-card__label">
                        <span class="pqr-capa-card__label-num">3</span>
                        Capa 3 — Texto Original
                    </div>
                    <blockquote class="pqr-texto-original">${capas.textoOriginal}</blockquote>
                </div>

            </div>

            <!-- Área de respuesta -->
            <div class="pqr-detail__response-area">
                <div class="pqr-response-textarea-wrapper">
                    <textarea
                        class="pqr-response-textarea"
                        id="pqr-response-textarea"
                        rows="2"
                        placeholder="Escribe tu respuesta o usa el precedente sugerido..."
                        aria-label="Campo de respuesta"
                    ></textarea>
                    <div class="pqr-response-actions">
                        <button class="pqr-response-tool-btn" aria-label="Adjuntar archivo" title="Adjuntar">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                        </button>
                        <button class="pqr-response-tool-btn" aria-label="Negrita" title="Negrita">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8"/></svg>
                        </button>
                    </div>
                </div>
                <button class="btn--enviar" id="btn-enviar-respuesta" aria-label="Enviar respuesta">
                    Enviar Respuesta
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
                </button>
            </div>
        </section>

        <!-- ── Panel derecho: Precedente + Ciudadano ── -->
        <aside class="pqr-right-panel" aria-label="Información adicional">

            <!-- Precedente encontrado -->
            <div>
                <div class="pqr-panel-section__label">
                    <span>Precedente encontrado</span>
                    <span class="pqr-panel-section__label-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M12 8h.01" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
                    </span>
                </div>

                <div class="pqr-precedente-card">
                    <div class="pqr-precedente-card__id">${precedente.id}</div>
                    <p class="pqr-precedente-card__resumen">${precedente.resumen}</p>
                    <button class="pqr-precedente-card__link" id="btn-ver-respuesta" aria-label="Ver respuesta del precedente">
                        Ver respuesta
                    </button>
                </div>

                <p class="pqr-similitud-badge">
                    Sugerencia basada en ${precedente.similitud}% de similitud temática.
                </p>
            </div>

            <!-- Info ciudadano -->
            <div class="pqr-ciudadano-card">
                <div class="pqr-ciudadano-card__icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                </div>
                <p class="pqr-ciudadano-card__texto">${ciudadanoMsg}</p>
            </div>

        </aside>
    `;
}

/* ── Toast helper ────────────────────────────────────────────────── */
function showToast(message, type = 'success') {
    let toast = document.getElementById('pqr-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'pqr-toast';
        toast.className = 'pqr-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `pqr-toast pqr-toast--${type}`;

    requestAnimationFrame(() => {
        toast.classList.add('pqr-toast--visible');
    });

    setTimeout(() => {
        toast.classList.remove('pqr-toast--visible');
    }, 3000);
}

/* ── Punto de entrada ────────────────────────────────────────────── */

/**
 * Renderiza el detalle completo de una PQR en containerEl.
 * @param {HTMLElement} containerEl
 * @param {string} pqrId
 */
export async function renderPqrDetail(containerEl, pqrId) {
    // Estado: cargando
    containerEl.innerHTML = `
        <section class="pqr-detail">
            <div class="pqr-loading">
                <div class="pqr-loading__spinner"></div>
                <p>Cargando PQR real...</p>
            </div>
        </section>
    `;

    let pqr;
    try {
        pqr = await getPqrDetails(pqrId);
    } catch (e) {
        console.error(e);
        containerEl.innerHTML = `
            <section class="pqr-detail">
                <div class="pqr-empty">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
                    <p>Error: ${e.message}</p>
                </div>
            </section>
        `;
        return;
    }

    containerEl.innerHTML = buildDetailHTML(pqr);

    // ── Eventos ──────────────────────────────────────────────────

    // Confirmar clasificación
    document.getElementById('btn-confirmar')?.addEventListener('click', async () => {
        const btn = document.getElementById('btn-confirmar');
        btn.disabled = true;
        btn.textContent = 'Confirmando...';
        try {
            await pqrsListService.confirm(pqr.radicado, pqr.tipo);
            showToast('✓ Clasificación confirmada exitosamente', 'success');
        } catch (e) {
            console.error(e);
            showToast('Error al confirmar clasificación', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                Confirmar clasificación
            `;
        }
    });

    // Ver respuesta precedente
    document.getElementById('btn-ver-respuesta')?.addEventListener('click', () => {
        const textarea = document.getElementById('pqr-response-textarea');
        if (textarea) {
            const analisis = pqr.analisis_ia || {};
            textarea.value = `[Basado en Precedente Sugerido]\nRespuesta estándar para solicitudes de ${analisis.secretaria_asignada || 'competencia general'}.`;
            textarea.focus();
        }
    });

    // Enviar respuesta
    document.getElementById('btn-enviar-respuesta')?.addEventListener('click', async () => {
        const textarea = document.getElementById('pqr-response-textarea');
        const texto = textarea?.value || '';
        const btn = document.getElementById('btn-enviar-respuesta');

        if (!texto.trim()) {
            showToast('La respuesta no puede estar vacía', 'error');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Enviando...';

        try {
            await pqrsListService.sendResponse(pqr.radicado, texto);
            showToast('✓ Respuesta enviada exitosamente', 'success');
            if (textarea) textarea.value = '';
        } catch (e) {
            console.error(e);
            showToast(e.message || 'Error al enviar respuesta', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = `
                Enviar Respuesta
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
            `;
        }
    });

    // Auto-resize textarea
    const textarea = document.getElementById('pqr-response-textarea');
    textarea?.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    });
}
