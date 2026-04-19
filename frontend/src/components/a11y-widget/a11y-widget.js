import './a11y-widget.css';

const FONT_SIZES = [14, 16, 18, 20, 22];
const FONT_DEFAULT_INDEX = 1;

const KEYS = {
    theme: 'pqrs_theme',
    fontIndex: 'pqrs_font_index',
};

let currentFontIndex = FONT_DEFAULT_INDEX;
let currentTheme = 'light';
let mediaListenerAttached = false;

export function renderA11yWidget() {
    const body = document.body;
    
    // Check if widget already exists to avoid duplicates
    if (document.getElementById('a11y-widget-container')) return;

    const widgetContainer = document.createElement('div');
    widgetContainer.id = 'a11y-widget-container';
    widgetContainer.className = 'a11y-widget-container';

    widgetContainer.innerHTML = `
        <div id="a11y-popup" class="a11y-popup" aria-hidden="true">
            <div class="a11y-popup-header">
                Ajustes de Accesibilidad
            </div>
            <div class="a11y-popup-body">
                <div class="a11y-setting">
                    <span class="a11y-setting-label">Tamaño de letra</span>
                    <div class="a11y-controls">
                        <button class="btn-a11y btn-font-down" data-a11y="font-down" aria-label="Disminuir tamaño de texto" title="Disminuir texto (A-)">A-</button>
                        <div class="font-level-indicator" aria-hidden="true">
                            <div class="font-level-dot"></div>
                            <div class="font-level-dot"></div>
                            <div class="font-level-dot"></div>
                            <div class="font-level-dot"></div>
                            <div class="font-level-dot"></div>
                        </div>
                        <button class="btn-a11y btn-font-up" data-a11y="font-up" aria-label="Aumentar tamaño de texto" title="Aumentar texto (A+)">A+</button>
                    </div>
                </div>
                <div class="a11y-setting">
                    <span class="a11y-setting-label">Tema Visual</span>
                    <button class="btn-a11y btn-theme" data-a11y="theme-toggle" aria-label="Cambiar tema" title="Cambiar tema">Cambiar</button>
                </div>
            </div>
        </div>
        <button id="a11y-toggle-btn" class="a11y-toggle-btn" aria-label="Abrir menú de accesibilidad" aria-expanded="false" aria-controls="a11y-popup">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </button>
    `;

    body.appendChild(widgetContainer);

    initA11yLogic();
}

function initA11yLogic() {
    const savedTheme = localStorage.getItem(KEYS.theme);
    if (savedTheme === 'dark' || savedTheme === 'light') {
        applyTheme(savedTheme);
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }

    const savedFontIndex = Number.parseInt(localStorage.getItem(KEYS.fontIndex), 10);
    const fontIndex = Number.isNaN(savedFontIndex)
        ? FONT_DEFAULT_INDEX
        : Math.min(Math.max(savedFontIndex, 0), FONT_SIZES.length - 1);

    applyFontSize(fontIndex);

    document.querySelectorAll('[data-a11y="font-up"]').forEach((btn) => {
        btn.onclick = increaseFontSize;
    });

    document.querySelectorAll('[data-a11y="font-down"]').forEach((btn) => {
        btn.onclick = decreaseFontSize;
    });

    document.querySelectorAll('[data-a11y="theme-toggle"]').forEach((btn) => {
        btn.onclick = toggleTheme;
    });

    if (!mediaListenerAttached) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
            if (!localStorage.getItem(KEYS.theme)) {
                applyTheme(event.matches ? 'dark' : 'light');
            }
        });
        mediaListenerAttached = true;
    }

    // Toggle popup
    const toggleBtn = document.getElementById('a11y-toggle-btn');
    const popup = document.getElementById('a11y-popup');
    
    toggleBtn.addEventListener('click', () => {
        const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
        toggleBtn.setAttribute('aria-expanded', !isExpanded);
        popup.setAttribute('aria-hidden', isExpanded);
        popup.classList.toggle('a11y-popup--visible');
    });

    // Close when clicking outside
    document.addEventListener('click', (event) => {
        if (!document.getElementById('a11y-widget-container').contains(event.target)) {
            toggleBtn.setAttribute('aria-expanded', 'false');
            popup.setAttribute('aria-hidden', 'true');
            popup.classList.remove('a11y-popup--visible');
        }
    });
}

function applyFontSize(index) {
    const size = FONT_SIZES[index];
    const scale = size / 16;

    document.documentElement.style.fontSize = `${size}px`;
    document.documentElement.style.setProperty('--font-scale', String(scale));

    updateFontButtons(index);
    localStorage.setItem(KEYS.fontIndex, String(index));

    currentFontIndex = index;
    announceToScreenReader(`Tamaño de fuente: nivel ${index + 1} de ${FONT_SIZES.length}`);
}

function increaseFontSize() {
    if (currentFontIndex < FONT_SIZES.length - 1) {
        applyFontSize(currentFontIndex + 1);
    }
}

function decreaseFontSize() {
    if (currentFontIndex > 0) {
        applyFontSize(currentFontIndex - 1);
    }
}

function updateFontButtons(index) {
    const btnUp = document.querySelector('[data-a11y="font-up"]');
    const btnDown = document.querySelector('[data-a11y="font-down"]');
    const dots = document.querySelectorAll('.font-level-dot');

    if (btnUp) {
        btnUp.disabled = index >= FONT_SIZES.length - 1;
    }

    if (btnDown) {
        btnDown.disabled = index <= 0;
    }

    dots.forEach((dot, i) => {
        dot.classList.toggle('font-level-dot--active', i <= index);
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    currentTheme = theme;

    const btnTheme = document.querySelector('[data-a11y="theme-toggle"]');
    if (btnTheme) {
        btnTheme.setAttribute('aria-label', theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
        btnTheme.textContent = theme === 'dark' ? 'Claro' : 'Oscuro';
    }

    localStorage.setItem(KEYS.theme, theme);
}

function toggleTheme() {
    applyTheme(currentTheme === 'light' ? 'dark' : 'light');
}

function announceToScreenReader(message) {
    let live = document.getElementById('a11y-live');

    if (!live) {
        live = document.createElement('div');
        live.id = 'a11y-live';
        live.setAttribute('aria-live', 'polite');
        live.setAttribute('aria-atomic', 'true');
        live.className = 'sr-only';
        document.body.appendChild(live);
    }

    setTimeout(() => {
        live.textContent = message;
    }, 100);
}

window.a11y = { toggleTheme, increaseFontSize, decreaseFontSize, applyTheme, applyFontSize };
