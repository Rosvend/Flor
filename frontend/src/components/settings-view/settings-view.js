import './settings-view.css';

/**
 * Renderiza la vista de configuración.
 * @param {HTMLElement} containerEl 
 */
export function renderSettingsView(containerEl) {
    containerEl.innerHTML = `
        <div class="settings-view">
            <header class="settings-view__header">
                <h1 class="settings-view__title">Configuración</h1>
                <p class="settings-view__subtitle">Personaliza tu entorno de trabajo y preferencias</p>
            </header>

            <!-- Sección: Interfaz -->
            <section class="settings-section">
                <h2 class="settings-section__title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2v20"/><path d="M12 12l8-8"/><path d="M12 12l8 8"/></svg>
                    Interfaz de Usuario
                </h2>
                
                <div class="settings-item">
                    <div class="settings-item__info">
                        <span class="settings-item__label">Tema Oscuro</span>
                        <span class="settings-item__desc">Aplica un esquema de colores de alto contraste optimizado para la vista.</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" checked disabled>
                        <span class="toggle-switch__slider"></span>
                    </label>
                </div>

                <div class="settings-item">
                    <div class="settings-item__info">
                        <span class="settings-item__label">Animaciones Fluídas</span>
                        <span class="settings-item__desc">Micro-interacciones y transiciones suaves en la plataforma.</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" checked>
                        <span class="toggle-switch__slider"></span>
                    </label>
                </div>
            </section>

            <!-- Sección: Notificaciones -->
            <section class="settings-section">
                <h2 class="settings-section__title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                    Notificaciones
                </h2>
                
                <div class="settings-item">
                    <div class="settings-item__info">
                        <span class="settings-item__label">Alertas por Correo</span>
                        <span class="settings-item__desc">Recibe un aviso cuando llegue una nueva PQRS a tu bandeja.</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" checked>
                        <span class="toggle-switch__slider"></span>
                    </label>
                </div>

                <div class="settings-item">
                    <div class="settings-item__info">
                        <span class="settings-item__label">Resúmenes Semanales</span>
                        <span class="settings-item__desc">Reporte consolidado de gestión y efectividad de respuesta.</span>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox">
                        <span class="toggle-switch__slider"></span>
                    </label>
                </div>
            </section>

            <!-- Sección: Organización -->
            <section class="settings-section">
                <h2 class="settings-section__title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                    Perfil Institucional
                </h2>
                
                <div class="settings-item">
                    <div class="settings-item__info">
                        <span class="settings-item__label">Nombre de la Entidad</span>
                        <span class="settings-item__desc">Alcaldía de Medellín - Secretaría de Seguridad</span>
                    </div>
                    <button class="settings-button--secondary" style="padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem;">Editar</button>
                </div>

                <div class="settings-item" style="border-bottom: none; margin-top: 1rem;">
                    <button class="settings-button">Guardar Cambios</button>
                </div>
            </section>
        </div>
    `;
}
