import './navbar.css';
import { storage } from '../../service/storage.js';

function activeClass(isActive) {
    return isActive ? 'navbar__link navbar__link--pill navbar__link--active' : 'navbar__link';
}

export function renderNavbar(options = {}) {
    const currentPath = options.currentPath || '/';
    const isLogin = currentPath === '/login';

    const homeLinkClass = activeClass(currentPath === '/');
    const pqrsLinkClass = activeClass(currentPath === '/pqrs');
    const adminLinkClass = activeClass(currentPath === '/admin/knowledge-base');

    const ctaHref = isLogin ? '/' : '/login';
    const ctaText = isLogin ? 'Volver al inicio' : 'Iniciar Sesion';

    const adminLink = storage.isAuthenticated()
        ? `<a href="/admin/knowledge-base" class="${adminLinkClass}" data-link>Base de conocimiento</a>`
        : '';

    return `
        <nav class="navbar" role="navigation" aria-label="Navegacion principal">
            <a href="/" class="navbar__brand" data-link>
                PQRS Medellin
            </a>

            <div class="navbar__center-links">
                <a href="/" class="${homeLinkClass}" data-link>Inicio</a>
                <a href="/pqrs" class="${pqrsLinkClass}" data-link>Radicar PQR</a>
                ${adminLink}
            </div>

            <a href="${ctaHref}" class="btn btn--accent btn--sm navbar__cta" data-link>${ctaText}</a>
        </nav>
    `;
}
