
import { renderHome } from '../pages/home/home.js'
import { renderLogin } from '../pages/login/login.js'
import { renderPqrs } from '../pages/pqrs/pqrs.js'
import { renderPqrsStatusLookup, renderPqrsStatusDetail } from '../pages/pqrs-status/pqrs-status.js'
import { renderAplicacion } from '../pages/aplicacion/aplicacion.js'
import { renderAdminKnowledgeBase } from '../pages/admin-knowledge-base/admin-knowledge-base.js'

const routes = {
    '/': renderHome,
    '/login': renderLogin,
    '/pqrs': renderPqrs,
    '/pqrs/estado': renderPqrsStatusLookup,
    '/aplicacion': renderAplicacion,
    '/admin/knowledge-base': renderAdminKnowledgeBase,
}

/* Rutas de prefijo — cualquier sub-ruta /aplicacion/:id también usa renderAplicacion */
const prefixRoutes = [
    { prefix: '/aplicacion/', renderer: renderAplicacion },
    { prefix: '/pqrs/estado/', renderer: renderPqrsStatusDetail },
]

/* ── FUNCIÓN RENDER ──
   Limpia el #app e invoca el renderer de la ruta actual.
   El fallback es la Home page (evita pantalla en blanco en 404). */
function render() {
    const path = window.location.pathname

    /* Buscar primero ruta exacta, luego ruta de prefijo */
    let page = routes[path]
    if (!page) {
        const match = prefixRoutes.find(r => path.startsWith(r.prefix))
        page = match ? match.renderer : renderHome
    }

    document.getElementById('app').innerHTML = ''
    page()

    /* Notificar a main.js que el DOM está listo para microinteracciones.
       Usamos requestAnimationFrame para dar al browser un ciclo de paint
       antes de medir posiciones (necesario para IntersectionObserver). */
       
    requestAnimationFrame(() => {
        window.dispatchEvent(new CustomEvent('page-rendered', { detail: { path } }))
    })
}

/* ── FUNCIÓN NAVIGATE ──
   Cambia la URL sin recargar la página (SPA).
   pushState no dispara el evento popstate — por eso llamamos render() manual. */
function navigate(path) {
    window.history.pushState({}, '', path)
    render()
}

/* ── FUNCIÓN INIT ──
   Se llama una sola vez desde main.js al cargar la app.
   Configura los 3 listeners y hace el primer render. */
function init() {
    /* Interceptar clicks en [data-link] para navegar sin recargar. */
    document.addEventListener('click', (e) => {
        const link = e.target.closest('[data-link]')
        if (link) {
            e.preventDefault()
            navigate(link.getAttribute('href'))
        }
    })

    /* Botones atrás/adelante del navegador. */
    window.addEventListener('popstate', render)

    /* Render inicial al cargar la URL directamente. */
    render()
}

export const router = { init, navigate }