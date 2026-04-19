import '../../../assets/main.css';
import './pqrs-status.css';
import { renderNavbar } from '../../components/navbar/navbar.js';
import { pqrsTrackingService } from '../../service/api.js';

function navigate(path) {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function normalizeRadicado(raw) {
    return String(raw || '').trim().toUpperCase();
}

function statusMeta(status) {
    const normalized = String(status || '').toUpperCase();
    const map = {
        RADICADA: { badge: 'badge badge--radicada', label: 'Radicada', step: 1 },
        EN_CLASIFICACION: { badge: 'badge badge--proceso', label: 'En clasificación', step: 2 },
        EN_GESTION: { badge: 'badge badge--proceso', label: 'En gestión', step: 3 },
        EN_REVISION_JURIDICA: { badge: 'badge badge--primaria', label: 'En revisión jurídica', step: 3 },
        RESPONDIDA: { badge: 'badge badge--resuelta', label: 'Respondida', step: 4 },
        CERRADA: { badge: 'badge badge--resuelta', label: 'Cerrada', step: 4 },
        VENCIDA: { badge: 'badge badge--rechazada', label: 'Vencida', step: 4 },
    };

    return map[normalized] || { badge: 'badge badge--primaria', label: normalized || 'Sin estado', step: 1 };
}

function timelineLabel(step) {
    const labels = {
        1: 'Radicada',
        2: 'Clasificación',
        3: 'Gestión interna',
        4: 'Respuesta al ciudadano',
    };
    return labels[step] || 'Paso';
}

function renderTimeline(step) {
    return `
        <div class="status-timeline" role="list" aria-label="Progreso de la solicitud">
            ${[1, 2, 3, 4].map((item) => {
                const isDone = item < step;
                const isCurrent = item === step;
                return `
                    <div class="status-step ${isDone ? 'is-done' : ''} ${isCurrent ? 'is-current' : ''}" role="listitem">
                        <div class="status-step__dot" aria-hidden="true"></div>
                        <span class="status-step__label">${timelineLabel(item)}</span>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function getResponseBlock(data) {
    if (!data.response || !data.response.message) {
        return `
            <section class="card tracking-section">
                <div class="card__header">
                    <h2 class="card__title">Respuesta oficial</h2>
                </div>
                <p class="text-secondary">Aún no hay una respuesta oficial cargada para esta PQR. Cuando sea emitida por la dependencia responsable aparecerá aquí.</p>
            </section>
        `;
    }

    return `
        <section class="card tracking-section">
            <div class="card__header">
                <h2 class="card__title">Respuesta oficial</h2>
                <span class="badge badge--resuelta">Disponible</span>
            </div>
            <p class="tracking-response__meta text-secondary">Fecha de respuesta: ${escapeHtml(data.response.responded_at || 'N/D')}</p>
            <div class="tracking-response__box">
                ${escapeHtml(data.response.message)}
            </div>
        </section>
    `;
}

function getAttachmentsList(items = []) {
    if (!items.length) {
        return '<p class="text-muted">Sin anexos registrados.</p>';
    }

    return `
        <ul class="tracking-attachments">
            ${items.map((item) => `<li>${escapeHtml(item.name || 'Adjunto')}</li>`).join('')}
        </ul>
    `;
}

export function renderPqrsStatusLookup() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <div class="mesh-bg" aria-hidden="true"></div>
        ${renderNavbar({ currentPath: '/pqrs' })}

        <main id="main-content" class="main-content tracking-main">
            <div class="container container--sm">
                <section class="card tracking-card">
                    <div class="card__header tracking-card__header">
                        <h1 class="card__title">Consultar Estado de PQR</h1>
                    </div>
                    <p class="text-secondary tracking-card__description">Ingresa tu número de radicado para ver el detalle de la solicitud, su estado actual y la respuesta oficial cuando esté disponible.</p>

                    <form id="tracking-form" class="tracking-form" novalidate>
                        <div class="form-group">
                            <label class="form-label form-label--required" for="tracking-radicado">Número de radicado</label>
                            <input
                                id="tracking-radicado"
                                name="radicado"
                                class="form-input"
                                type="text"
                                placeholder="Ej: RAD-2026-123456"
                                autocomplete="off"
                                required
                            >
                            <p class="form-hint">Puedes usar mayúsculas o minúsculas. El sistema lo normaliza automáticamente.</p>
                        </div>

                        <div id="tracking-error" class="tracking-error hidden" role="alert"></div>

                        <div class="tracking-form__actions">
                            <a href="/" class="btn btn--ghost" data-link>Volver al inicio</a>
                            <button type="submit" class="btn btn--primary">Consultar estado</button>
                        </div>
                    </form>
                </section>
            </div>
        </main>
    `;

    const form = document.getElementById('tracking-form');
    const input = document.getElementById('tracking-radicado');
    const errorBox = document.getElementById('tracking-error');

    form?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const radicado = normalizeRadicado(input?.value);

        errorBox?.classList.add('hidden');
        errorBox.textContent = '';

        if (!radicado) {
            errorBox.textContent = 'Debes ingresar un número de radicado para continuar.';
            errorBox.classList.remove('hidden');
            return;
        }

        try {
            // Optional pre-check to provide immediate feedback before navigation.
            await pqrsTrackingService.checkExists(radicado);
            navigate(`/pqrs/estado/${encodeURIComponent(radicado)}`);
        } catch (error) {
            errorBox.textContent = error?.message || 'No fue posible validar el radicado en este momento.';
            errorBox.classList.remove('hidden');
        }
    });
}

export async function renderPqrsStatusDetail() {
    const app = document.getElementById('app');
    const path = window.location.pathname;
    const encodedRadicado = path.split('/pqrs/estado/')[1] || '';
    const radicado = normalizeRadicado(decodeURIComponent(encodedRadicado));

    app.innerHTML = `
        <div class="mesh-bg" aria-hidden="true"></div>
        ${renderNavbar({ currentPath: '/pqrs' })}

        <main id="main-content" class="main-content tracking-main">
            <div class="container container--md">
                <section class="card tracking-card tracking-card--loading">
                    <p class="text-secondary">Cargando estado para ${escapeHtml(radicado || 'radicado')}...</p>
                </section>
            </div>
        </main>
    `;

    if (!radicado) {
        navigate('/pqrs/estado');
        return;
    }

    try {
        const data = await pqrsTrackingService.getByRadicado(radicado);
        const meta = statusMeta(data.status);

        app.innerHTML = `
            <div class="mesh-bg" aria-hidden="true"></div>
            ${renderNavbar({ currentPath: '/pqrs' })}

            <main id="main-content" class="main-content tracking-main">
                <div class="container container--md tracking-layout">
                    <section class="card tracking-section">
                        <div class="card__header tracking-header">
                            <h1 class="card__title">Radicado ${escapeHtml(data.radicado)}</h1>
                            <span class="${meta.badge}">${meta.label}</span>
                        </div>
                        <p class="text-secondary">Fecha de radicación: ${escapeHtml(data.created_at || 'N/D')}</p>

                        ${renderTimeline(meta.step)}
                    </section>

                    <section class="card tracking-section">
                        <div class="card__header">
                            <h2 class="card__title">Solicitud enviada</h2>
                        </div>
                        <div class="tracking-grid">
                            <div>
                                <p class="tracking-key">Tipo</p>
                                <p class="tracking-value">${escapeHtml(data.type || 'N/D')}</p>
                            </div>
                            <div>
                                <p class="tracking-key">Asunto</p>
                                <p class="tracking-value">${escapeHtml(data.subject || 'N/D')}</p>
                            </div>
                            <div>
                                <p class="tracking-key">Canal</p>
                                <p class="tracking-value">${escapeHtml(data.channel || 'N/D')}</p>
                            </div>
                            <div>
                                <p class="tracking-key">Dependencia</p>
                                <p class="tracking-value">${escapeHtml(data.assigned_to || 'Pendiente de asignación')}</p>
                            </div>
                        </div>

                        <div class="tracking-description">
                            <p class="tracking-key">Descripción registrada</p>
                            <p class="tracking-text">${escapeHtml(data.description || 'Sin descripción')}</p>
                        </div>

                        <div class="tracking-attachments-wrap">
                            <p class="tracking-key">Anexos</p>
                            ${getAttachmentsList(data.attachments || [])}
                        </div>
                    </section>

                    ${getResponseBlock(data)}

                    <div class="tracking-actions">
                        <a href="/pqrs/estado" class="btn btn--secondary" data-link>Consultar otro radicado</a>
                        <a href="/" class="btn btn--ghost" data-link>Volver al inicio</a>
                    </div>
                </div>
            </main>
        `;
    } catch (error) {
        app.innerHTML = `
            <div class="mesh-bg" aria-hidden="true"></div>
            ${renderNavbar({ currentPath: '/pqrs' })}

            <main id="main-content" class="main-content tracking-main">
                <div class="container container--sm">
                    <section class="card tracking-card tracking-card--error">
                        <h1 class="card__title">No encontramos ese radicado</h1>
                        <p class="text-secondary">${escapeHtml(error?.message || 'Verifica el número e inténtalo nuevamente.')}</p>
                        <div class="tracking-form__actions">
                            <a href="/pqrs/estado" class="btn btn--primary" data-link>Intentar de nuevo</a>
                            <a href="/" class="btn btn--ghost" data-link>Volver al inicio</a>
                        </div>
                    </section>
                </div>
            </main>
        `;
    }
}
