import './navbar.css';
import alcaldiaLogo from '../../../assets/alcaldialogo.png';
import { storage } from '../../service/storage.js';

function activeClass(isActive) {
    return isActive ? 'navbar__link navbar__link--pill navbar__link--active' : 'navbar__link';
}

export function renderNavbar(options = {}) {
    const currentPath = options.currentPath || '/';
    const isLogin = currentPath === '/login';

    const homeLinkClass = activeClass(currentPath === '/');
    const pqrsLinkClass = activeClass(currentPath === '/pqrs');
    const adminKbLinkClass = activeClass(currentPath === '/admin/knowledge-base');

    const ctaHref = isLogin ? '/' : '/login';
    const ctaText = isLogin ? 'Volver al inicio' : 'Iniciar Sesion';

    // Only authenticated users can reach the knowledge-base upload page.
    const adminKbLinkHTML = storage.isAuthenticated()
        ? `<a href="/admin/knowledge-base" class="${adminKbLinkClass}" data-link>Base de conocimiento</a>`
        : '';

    return `
        <div class="topbar-gov">
            <div class="topbar-gov__inner">
                <img
                    src="https://cdnwordpresstest-f0ekdgevcngegudb.z01.azurefd.net/es/wp-content/themes/theme_alcaldia/img/logo_gov.png"
                    alt="Gov.co"
                    class="topbar-gov__logo"
                >
            </div>
        </div>
        <nav class="navbar" role="navigation" aria-label="Navegacion principal">
            <a href="/" class="navbar__brand" data-link>
                <span class="navbar__brand-text"><span class="navbar__brand-flor">Flor</span> te escucha</span>
                <img src="${alcaldiaLogo}" alt="Alcaldía de Medellín" class="navbar__alcaldia-logo">
            </a>

            <div class="navbar__center-links">
                <a href="/" class="${homeLinkClass}" data-link>Inicio</a>
                <a href="/pqrs" class="${pqrsLinkClass}" data-link>Radicar PQR</a>
                ${adminKbLinkHTML}
            </div>

            <a href="${ctaHref}" class="btn btn--accent btn--sm navbar__cta" data-link>${ctaText}</a>
        </nav>
    `;
}
