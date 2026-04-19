import './navbar.css';

function activeClass(isActive) {
    return isActive ? 'navbar__link navbar__link--pill navbar__link--active' : 'navbar__link';
}

export function renderNavbar(options = {}) {
    const currentPath = options.currentPath || '/';
    const isLogin = currentPath === '/login';

    const homeLinkClass = activeClass(currentPath === '/');
    const pqrsLinkClass = activeClass(currentPath === '/pqrs');

    const ctaHref = isLogin ? '/' : '/login';
    const ctaText = isLogin ? 'Volver al inicio' : 'Iniciar Sesion';

    return `
        <nav class="navbar" role="navigation" aria-label="Navegacion principal">
            <a href="/" class="navbar__brand" data-link>
                PQRS Medellin
            </a>

            <div class="navbar__center-links">
                <a href="/" class="${homeLinkClass}" data-link>Inicio</a>
                <a href="/pqrs" class="${pqrsLinkClass}" data-link>Radicar PQR</a>
            </div>

            <a href="${ctaHref}" class="btn btn--accent btn--sm navbar__cta" data-link>${ctaText}</a>
        </nav>
    `;
}
