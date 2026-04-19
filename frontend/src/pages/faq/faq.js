import '../../../assets/main.css';
import './faq.css';
import { renderNavbar } from '../../components/navbar/navbar.js';

export function renderFaq() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <a class="skip-link" href="#main-content">Saltar al contenido principal</a>

        ${renderNavbar({ currentPath: '/faq' })}

        <main id="main-content" class="faq-layout">
            <header class="faq-hero">
                <div class="faq-container">
                    <h1 class="faq-title">Centro de Ayuda al Ciudadano</h1>
                    <p class="faq-subtitle">Encuentra respuestas rápidas sobre cómo radicar y hacer seguimiento a tus Peticiones, Quejas, Reclamos, Sugerencias y Denuncias (PQRSD).</p>
                </div>
            </header>

            <section class="faq-section faq-container">
                <div class="faq-grid">
                    
                    <article class="faq-card">
                        <div class="faq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-text"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
                        </div>
                        <h2 class="faq-card-title">¿Qué es una PQRSD?</h2>
                        <ul class="faq-list">
                            <li><strong>Petición:</strong> Solicitud formal de información o servicios.</li>
                            <li><strong>Queja:</strong> Inconformidad con un servidor público o atención.</li>
                            <li><strong>Reclamo:</strong> Inconformidad por un servicio deficiente.</li>
                            <li><strong>Sugerencia:</strong> Recomendación para mejorar nuestro servicio.</li>
                            <li><strong>Denuncia:</strong> Reporte de posibles actos de corrupción o delitos.</li>
                        </ul>
                    </article>

                    <article class="faq-card">
                        <div class="faq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-send"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
                        </div>
                        <h2 class="faq-card-title">¿Cómo radicar una nueva solicitud?</h2>
                        <p class="faq-text">
                            Puedes explorar nuestros diferentes canales oficiales:
                        </p>
                        <ol class="faq-list faq-list-numbered">
                            <li>De forma virtual usando nuestro <strong>formulario web</strong>.</li>
                            <li>Hablando con nuestra asistente virtual <strong>Flor</strong> vía WhatsApp al +57 3016044444.</li>
                            <li>Enviando un mensaje directo a nuestras <strong>redes sociales</strong> institucionales.</li>
                        </ol>
                        <p class="faq-text">El sistema te generará un número de Radicado único tras el envío.</p>
                    </article>

                    <article class="faq-card">
                        <div class="faq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                        </div>
                        <h2 class="faq-card-title">¿Cómo consultar mi estado?</h2>
                        <p class="faq-text">
                            Para hacer seguimiento a tu solicitud, ve a la sección de <strong>estado</strong> en el menú de navegación superior.
                        </p>
                        <p class="faq-text">
                            Ingresa tu número de <strong>Radicado (Ej: RAD-2026-123456)</strong>. Podrás ver en tiempo real en qué área de la Alcaldía se encuentra, la etapa de resolución y actualizaciones disponibles. 
                        </p>
                    </article>

                    <article class="faq-card">
                        <div class="faq-icon-wrapper">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        </div>
                        <h2 class="faq-card-title">Tiempos de respuesta legales</h2>
                        <p class="faq-text">
                            Según la Ley 1755 de 2015, los tiempos máximos fijados son (días hábiles):
                        </p>
                        <ul class="faq-list">
                            <li><strong>Peticiones de información:</strong> 10 días.</li>
                            <li><strong>Quejas, Reclamos y Sugerencias:</strong> 15 días.</li>
                            <li><strong>Denuncias por corrupción:</strong> 15 días.</li>
                            <li><strong>Consultas jurídicas:</strong> 30 días.</li>
                        </ul>
                    </article>

                 </div>
                 
                 <div class="faq-cta-container">
                    <h3 class="faq-cta-title">¿Todo listo?</h3>
                    <div class="faq-btn-group">
                        <a href="/pqrs" class="btn btn--primary btn--lg" data-link>Radicar PQRSD</a>
                        <a href="/pqrs/estado" class="btn btn--outline-dark btn--lg" data-link>Consultar estado</a>
                    </div>
                 </div>
            </section>
        </main>
    `;
}