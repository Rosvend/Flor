import '../../../assets/main.css';
import './home.css';
import { renderNavbar } from '../../components/navbar/navbar.js';
import chatbotImg from '../../../assets/fotochatbot.png';
import bannerVideo from '../../../assets/banner.mp4';
import { chatbotService } from '../../service/api.js';

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

            <!-- Chatbot Section -->
            <section class="chatbot-mobile-panel" id="chatbot-mobile-panel">
                <div class="chatbot-floating-wrapper">
                    <button class="chatbot-img-btn" aria-label="Hablar con Flor chatbot">
                        <img src="${chatbotImg}" alt="Flor chatbot">
                    </button>
                    <div class="chatbot-bubble">
                        ¡Asegurate de hablar<br>con FLOR antes<br>de crear tu PQR!
                    </div>
                </div>
                <div class="chatbot-window" id="chatbot-window">
                    <div class="chatbot-header">
                        <div class="chatbot-header-info">
                            <img src="${chatbotImg}" alt="Flor" class="chatbot-header-avatar">
                            <div>
                                <h3 class="chatbot-header-title">Flor</h3>
                                <span class="chatbot-header-status">En línea</span>
                            </div>
                        </div>
                        <button class="chatbot-close-btn" id="chatbot-close-btn" aria-label="Cerrar chat">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                        </button>
                    </div>
                    <div class="chatbot-messages" id="chatbot-messages">
                        <div class="chat-message chat-message--bot">
                            ¡Hola! Soy Flor, la asistente virtual de la Alcaldía de Medellín. ¿En qué te puedo ayudar hoy?
                        </div>
                    </div>
                    <form class="chatbot-input-area" id="chatbot-form">
                        <input type="text" class="chatbot-input" id="chatbot-input" placeholder="Escribe tu mensaje..." required>
                        <button type="submit" class="chatbot-send-btn" aria-label="Enviar mensaje">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
                        </button>
                    </form>
                </div>
            </section>

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

                    <a href="/pqrs/estado" class="action-card-new" data-link>
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

    // Chatbot Logic
    const chatbotWrapper = document.querySelector('.chatbot-floating-wrapper');
    const chatbotMobilePanel = document.getElementById('chatbot-mobile-panel');
    const chatbotBtn = document.querySelector('.chatbot-img-btn');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotCloseBtn = document.getElementById('chatbot-close-btn');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    if (!chatbotBtn || !chatbotWindow) return;

    chatbotWrapper.addEventListener('click', () => {
        if (chatbotWrapper.classList.contains('is-open')) return;
        chatbotWrapper.classList.add('is-open');
        chatbotMobilePanel?.classList.add('is-open');
        setTimeout(() => {
            chatbotWindow.classList.add('is-active');
            chatbotInput.focus();
        }, 500);
    });

    chatbotCloseBtn.addEventListener('click', () => {
        chatbotWindow.classList.remove('is-active');
        setTimeout(() => {
            chatbotWrapper.classList.remove('is-open');
            chatbotMobilePanel?.classList.remove('is-open');
        }, 300);
    });

    function appendBotReply({ answer, used_fallback }) {
        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = used_fallback
            ? 'chat-message chat-message--bot chat-message--fallback'
            : 'chat-message chat-message--bot';
        botMsgDiv.textContent = answer;
        chatbotMessages.appendChild(botMsgDiv);

        if (used_fallback) {
            const cta = document.createElement('a');
            cta.className = 'chat-message-cta';
            cta.href = '/pqrs';
            cta.setAttribute('data-link', '');
            cta.textContent = 'Radicar PQRSD';
            chatbotMessages.appendChild(cta);
        }
    }

    chatbotForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userText = chatbotInput.value.trim();
        if (!userText) return;

        const userMsgDiv = document.createElement('div');
        userMsgDiv.className = 'chat-message chat-message--user';
        userMsgDiv.textContent = userText;
        chatbotMessages.appendChild(userMsgDiv);
        chatbotInput.value = '';
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-loading';
        loadingDiv.innerHTML = '<div class="chat-loading-dot"></div><div class="chat-loading-dot"></div><div class="chat-loading-dot"></div>';
        chatbotMessages.appendChild(loadingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

        try {
            const res = await chatbotService.query(userText);
            chatbotMessages.removeChild(loadingDiv);
            appendBotReply(res);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        } catch (error) {
            if (chatbotMessages.contains(loadingDiv)) {
                chatbotMessages.removeChild(loadingDiv);
            }
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chat-message chat-message--bot';
            errorDiv.style.color = 'var(--color-danger)';
            errorDiv.textContent = "Lo siento, hubo un error de conexión con el servicio.";
            chatbotMessages.appendChild(errorDiv);
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    });
}
