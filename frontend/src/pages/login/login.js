import '../../../assets/main.css';
import './login.css';
import { renderNavbar } from '../../components/navbar/navbar.js';
import { authService, ApiError } from '../../service/api.js';

export function renderLogin() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <div class="mesh-bg" aria-hidden="true"></div>

        ${renderNavbar({ currentPath: '/login' })}

        <main id="main-content" class="main-content login-main">
            <div class="container login-container">
                <div class="card login-card">
                    <div class="card__header login-header">
                        <h1 class="card__title login-title">Iniciar Sesión</h1>
                        <p class="text-secondary text-sm">Accede a tu cuenta para continuar</p>
                    </div>
                    
                    <form id="login-form" class="login-form">
                        <div id="login-error" class="form-error-box hidden"></div>
                        <div class="form-group">
                            <label for="email" class="form-label form-label--required">Correo electrónico</label>
                            <input type="email" id="email" class="form-input" placeholder="ejemplo@correo.com" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="password" class="form-label form-label--required">Contraseña</label>
                            <input type="password" id="password" class="form-input" placeholder="••••••••" required>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn--accent btn--lg login-btn">Entrar</button>
                        </div>
                    </form>
                </div>
            </div>
        </main>
    `;

    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        loginError.classList.add('hidden');
        loginError.textContent = '';

        const correoElectronico = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        try {
            await authService.login(correoElectronico, password);
            window.history.pushState({}, '', '/aplicacion');
            window.dispatchEvent(new PopStateEvent('popstate'));
        } catch (error) {
            const message = error instanceof ApiError ? error.message : 'No se pudo iniciar sesión. Verifica el backend.';
            loginError.textContent = message;
            loginError.classList.remove('hidden');
        }
    });
}
