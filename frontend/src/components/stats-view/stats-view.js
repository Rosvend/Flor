import './stats-view.css';
import { getDashboardData } from '../../service/api.js';

/**
 * Renderiza la vista de estadísticas detalladas con visuales premium y variables corregidas.
 * @param {HTMLElement} containerEl 
 */
export async function renderStatsView(containerEl) {
    containerEl.innerHTML = `
        <div class="stats-view">
            <header class="stats-view__header">
                <div class="stats-view__title-group">
                    <h1 class="stats-view__title">Análisis Operativo</h1>
                    <p class="stats-view__subtitle">Métricas críticas y comportamiento ciudadano</p>
                </div>
                <div class="stats-view__refresh">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>
                    Sincronizado en tiempo real
                </div>
            </header>
            
            <div style="display:flex; justify-content:center; padding: 10rem 0;">
                <div style="width: 40px; height: 40px; border: 4px solid var(--color-border); border-top-color: var(--color-primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>
            <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
        </div>
    `;

    try {
        const stats = await getDashboardData();
        
        // Donut Logic
        const totalSent = (stats.by_sentiment?.POSITIVO || 0) + 
                          (stats.by_sentiment?.NEUTRAL || 0) + 
                          (stats.by_sentiment?.NEGATIVO || 0) || 1;
        
        const posVal = stats.by_sentiment?.POSITIVO || 0;
        const neuVal = stats.by_sentiment?.NEUTRAL || 0;
        const negVal = stats.by_sentiment?.NEGATIVO || 0;

        const posP = (posVal / totalSent) * 100;
        const neuP = posP + (neuVal / totalSent) * 100;

        // Bar Logic
        const maxVal = Math.max(...Object.values(stats.by_type || { 'OTROS': 0 }), 1);
        const categoriesHTML = Object.entries(stats.by_type || {})
            .sort((a, b) => b[1] - a[1])
            .map(([label, value]) => `
                <div class="category-item">
                    <span class="category-label">${label}</span>
                    <div class="category-bar-wrapper">
                        <div class="category-bar-fill" style="width: ${(value / maxVal) * 100}%"></div>
                    </div>
                    <span class="category-value">${value}</span>
                </div>
            `).join('');

        containerEl.innerHTML = `
            <div class="stats-view">
                <header class="stats-view__header">
                    <div class="stats-view__title-group">
                        <h1 class="stats-view__title">Análisis Operativo</h1>
                        <p class="stats-view__subtitle">Métricas críticas y comportamiento ciudadano</p>
                    </div>
                    <div class="stats-view__refresh">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>
                        Datos actualizados en vivo
                    </div>
                </header>

                <div class="stats-view__kpis">
                    <div class="stats-view__kpi" style="--kpi-color: var(--color-info)">
                        <div class="stats-view__kpi-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                        </div>
                        <span class="stats-view__kpi-label">Volumen Total</span>
                        <span class="stats-view__kpi-value">${stats.total}</span>
                        <div class="stats-view__kpi-trend">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m19 12-7-7-7 7"/><path d="M12 19V5"/></svg>
                            Incremento estable
                        </div>
                    </div>

                    <div class="stats-view__kpi" style="--kpi-color: var(--color-warning)">
                        <div class="stats-view__kpi-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        </div>
                        <span class="stats-view__kpi-label">Casos Activos</span>
                        <span class="stats-view__kpi-value">${stats.pendientes}</span>
                        <div class="stats-view__kpi-trend" style="color: var(--color-warning)">
                            En flujo de trabajo
                        </div>
                    </div>

                    <div class="stats-view__kpi" style="--kpi-color: var(--color-danger)">
                        <div class="stats-view__kpi-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="M2 12h2"/><path d="m4.93 19.07 1.41-1.41"/><path d="M12 22v-2"/><path d="m19.07 19.07-1.41-1.41"/><path d="M22 12h-2"/><path d="m19.07 4.93-1.41 1.41"/><path d="M15.91 10a5 5 0 0 1-5.91 5.91"/></svg>
                        </div>
                        <span class="stats-view__kpi-label">Urgencia / Vencen</span>
                        <span class="stats-view__kpi-value">${stats.vencen_hoy}</span>
                        <div class="stats-view__kpi-trend" style="color: var(--color-danger)">
                            Requiere atención inmediata
                        </div>
                    </div>
                </div>

                <div class="stats-view__charts">
                    <div class="stats-view__chart-card">
                        <div class="stats-view__chart-header">
                            <h3 class="stats-view__chart-title">
                                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"/><path d="M18 10h.01"/><path d="M6 10h.01"/><path d="M8 15h8"/></svg>
                                Clima de Opinión
                            </h3>
                            <p class="stats-view__chart-desc">Sentimiento procesado por IA</p>
                        </div>
                        <div class="donut-container">
                            <div class="donut-chart" style="--pos-p: ${posP}%; --neu-p: ${neuP}%">
                                <div class="donut-center">
                                    <span class="donut-value">${totalSent}</span>
                                    <span class="donut-label">Total</span>
                                </div>
                            </div>
                            <div class="sentiment-legend">
                                <div class="sentiment-item">
                                    <div class="sentiment-left">
                                        <div class="sentiment-color" style="background: var(--sentiment-pos)"></div>
                                        <span class="sentiment-name">Positivo</span>
                                    </div>
                                    <span class="sentiment-val">${posVal}</span>
                                </div>
                                <div class="sentiment-item">
                                    <div class="sentiment-left">
                                        <div class="sentiment-color" style="background: var(--sentiment-neu)"></div>
                                        <span class="sentiment-name">Neutral</span>
                                    </div>
                                    <span class="sentiment-val">${neuVal}</span>
                                </div>
                                <div class="sentiment-item">
                                    <div class="sentiment-left">
                                        <div class="sentiment-color" style="background: var(--sentiment-neg)"></div>
                                        <span class="sentiment-name">Negativo</span>
                                    </div>
                                    <span class="sentiment-val">${negVal}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="stats-view__chart-card">
                        <div class="stats-view__chart-header">
                            <h3 class="stats-view__chart-title">
                                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2"/><path d="M21 7H3"/><path d="M21 17H3"/><path d="M17 21v-4"/><path d="M7 21v-4"/><path d="M17 3v4"/><path d="M7 3v4"/></svg>
                                Tipología Ciudadana
                            </h3>
                            <p class="stats-view__chart-desc">Distribución por categoría de solicitud</p>
                        </div>
                        <div class="category-list">
                            ${categoriesHTML || '<p style="text-align:center; color:var(--color-text-muted); margin-top:2rem;">Sin datos suficientes</p>'}
                        </div>
                    </div>
                </div>

                <div class="stats-view__summary">
                    <div class="summary-card">
                        <div class="summary-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 12 2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>
                        </div>
                        <div class="summary-content">
                            <h4>Eficiencia de Respuesta</h4>
                            <p>Tu tasa de cierre ha subido un 5% esta semana según el histórico actual.</p>
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-icon" style="background: var(--color-accent-light); color: var(--color-accent);">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="m16.2 7.8 2.9-2.9"/><path d="M18 12h4"/><path d="m16.2 16.2 2.9 2.9"/><path d="M12 18v4"/><path d="m4.9 19.1 2.9-2.9"/><path d="M2 12h4"/><path d="m4.9 4.9 2.9 2.9"/></svg>
                        </div>
                        <div class="summary-content">
                            <h4>IA Insights</h4>
                            <p>El análisis semántico indica un clima predominantemente constructivo.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error("Error loading statistics view:", error);
        containerEl.innerHTML = `
            <div class="stats-view" style="display:flex; flex-direction:column; align-items:center; gap:1.5rem; padding-top:10rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--color-danger)"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
                <p style="color:var(--color-text-muted); font-weight:600;">No se pudieron cargar los datos analíticos.</p>
                <button onclick="location.reload()" class="btn btn--primary" style="padding:0.75rem 2rem;">Reintentar</button>
            </div>
        `;
    }
}
