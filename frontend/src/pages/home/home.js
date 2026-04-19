import '../../../assets/main.css';
import './home.css';
import { renderNavbar } from '../../components/navbar/navbar.js';
import chatbotImg from '../../../assets/fotochatbot.png';
import bannerVideo from '../../../assets/banner.mp4';

export function renderHome() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <a class="skip-link" href="#main-content">Saltar al contenido principal</a>

        <div class="mesh-bg" aria-hidden="true"></div>

        ${renderNavbar({ currentPath: '/' })}

        <main id="main-content" class="home-layout-new">
            
            <!-- Left Column -->
            <div class="home-col-new home-col--left">
                <div class="home-col-content-new">
                    <div class="portal-tag">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                        PORTAL CIUDADANO
                    </div>
                    
                    <h1 class="home-title-new">
                        Tu voz construye<br>
                        <span class="highlight-text">nuestra ciudad</span>
                    </h1>
                    
                    <p class="home-paragraph-new">
                        Registra y haz seguimiento a tus peticiones, reclamos y sugerencias de manera ágil. escucharte y mejorar Medellín juntos.
                    </p>
                    
                    <a href="#" class="btn btn--outline-dark btn--lg">Conoce más</a>
                </div>
            </div>
            
            <!-- Center Chatbot Floating Element -->
            <div class="chatbot-floating-wrapper">
                <button class="chatbot-img-btn" aria-label="Hablar con Flor chatbot">
                    <img src="${chatbotImg}" alt="Flor chatbot">
                </button>
                <div class="chatbot-bubble">
                    Habla con Flor<br>antes de crear<br>tu pqr
                </div>
            </div>

            <!-- Right Column (Video Background) -->
            <div class="home-col-new home-col--right">
                <video autoplay loop muted playsinline class="bg-video">
                    <source src="${bannerVideo}" type="video/mp4">
                </video>
                <div class="bg-video-overlay"></div>
                
                <div class="home-cards-wrapper-new">
                    <a href="/pqrs" class="action-card-new" data-link>
                        <div class="action-card-icon-new">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="none" class="lucide lucide-file-pen"><path d="M12 22h6a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v10"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10.4 12.6a2 2 0 1 1 3 3L8 21l-4 1 1-4Z"/></svg>
                        </div>
                        <div class="action-card-text-new">
                            <h3>Radicar PQR</h3>
                            <p>Inicia una nueva solicitud, queja, reclamo o sugerencia formal.</p>
                            <span class="card-link-text">Empezar ahora <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
                        </div>
                    </a>

                    <a href="#" class="action-card-new">
                        <div class="action-card-icon-new">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                        </div>
                        <div class="action-card-text-new">
                            <h3>Ver estado</h3>
                            <p>Consulta el avance de tus solicitudes previas con tu número de radicado.</p>
                            <span class="card-link-text">Consultar <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
                        </div>
                    </a>
                </div>
            </div>
            
        </main>

        <footer class="footer-simple">
            <div class="container footer-simple-flex">
                <span class="copyright">© 2024 ALCALDÍA DE MEDELLÍN - DISTRITO DE CIENCIA, TECNOLOGÍA E INNOVACIÓN</span>
                <div class="footer-simple-links">
                    <a href="#">PRIVACIDAD</a>
                    <a href="#">TÉRMINOS Y CONDICIONES</a>
                    <a href="#">MAPA DEL SITIO</a>
                </div>
            </div>
        </footer>
    `;
}
