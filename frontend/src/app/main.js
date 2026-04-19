import { router } from './router.js'
import { renderA11yWidget } from '../components/a11y-widget/a11y-widget.js'

document.addEventListener('DOMContentLoaded', () => {

    router.init()
    
    // Initialize the accessibility widget globally
    renderA11yWidget()

    /* Ocultar el widget de accesibilidad en la página /aplicacion
       ya que tiene su propio layout full-screen sin espacio para el widget flotante */
    window.addEventListener('page-rendered', ({ detail }) => {
        const widgetContainer = document.getElementById('a11y-widget-container')
        if (!widgetContainer) return
        const isAppPage = detail?.path?.startsWith('/aplicacion')
        widgetContainer.style.display = isAppPage ? 'none' : ''
    })
})
