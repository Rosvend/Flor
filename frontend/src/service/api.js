import { storage } from './storage.js'
import { USE_MOCK, mockAuth, mockPqrs, mockChatbot } from './mock.js'

export const BASE_URL = 'http://127.0.0.1:8000/api/v1'
export const AUTH_CHANGED_EVENT = 'auth-changed'
export const AUTH_EXPIRED_EVENT = 'auth-expired' 
export const AUTH_FORBIDDEN_EVENT = 'auth-forbidden' // Evento para manejar acceso denegado por roles

// ─── Clases de Errores Específicos ──────────────────────────────
export class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

export class NetworkError extends Error {
    constructor(message) {
        super(message);
        this.name = 'NetworkError';
    }
}

export class TimeoutError extends Error {
    constructor(message) {
        super(message);
        this.name = 'TimeoutError';
    }
}

export class ForbiddenError extends Error {
    constructor(message, data) {
        super(message);
        this.name = 'ForbiddenError';
        this.status = 403;
        this.data = data;
    }
}

export function emitAuthChanged() {
    window.dispatchEvent(new CustomEvent(AUTH_CHANGED_EVENT, {
        detail: { authenticated: storage.isAuthenticated() },
    }))
}

// ─── Mutex para el Refresh Token ────────────────────────────────
let refreshPromise = null;

async function refreshAccessToken() {
    try {
        const refreshToken = storage.getRefreshToken()
        if (!refreshToken) return false

        const response = await fetch(`${BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'refresh-token': refreshToken },
        })

        if (!response.ok) return false

        const tokenData = await response.json()
        const newAccessToken  = tokenData.access_token  || tokenData.accessToken  || tokenData
        const newRefreshToken = tokenData.refresh_token || tokenData.refreshToken || refreshToken
        storage.setTokens(newAccessToken, newRefreshToken)
        return true

    } catch {
        return false
    }
}

// ─── Función Principal de Peticiones (Refactorizada y Robusta) ──

/**
 * Cliente avanzado para consumo del backend.
 * Soporta query params, timeouts, formData, refresh automático y cancelación.
 * 
 * @param {string} endpoint - Ejemplo: '/users'
 * @param {Object} options - Configuración
 * @param {string} [options.method='GET']
 * @param {Object|FormData} [options.data=null] - Body (JSON o FormData)
 * @param {Object} [options.params=null] - Query params url
 * @param {boolean} [options.requiresAuth=false] - Usa Bearer token
 * @param {Object} [options.headers={}] - Headers extras
 * @param {number} [options.timeout=10000] - Tiempo máximo en ms
 * @param {boolean} [options._isRetry=false] - (Uso Interno)
 */
export async function request(endpoint, options = {}) {
    const {
        method = 'GET',
        data = null,
        params = null,
        requiresAuth = false,
        headers = {},
        timeout = 10000,
        _isRetry = false,
        ...customConfig
    } = options;

    let url = `${BASE_URL}${endpoint}`;

    // 1. Manejo Automático de Query Params
    if (params) {
        const searchParams = new URLSearchParams(params);
        const queryString = searchParams.toString();
        if (queryString) {
            url += `?${queryString}`;
        }
    }

    const config = {
        method,
        headers: { ...headers },
        ...customConfig,
    };

    // 2. Inyección de Headers de Autenticación
    if (requiresAuth) {
        const token = storage.getAccessToken();
        if (!token) throw new ApiError('No hay token de acceso local. Por favor inicia sesión.', 401, null);
        config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 3. Manejo Inteligente del Body (FormData vs JSON)
    if (data) {
        if (data instanceof FormData) {
            config.body = data;
            // No forzamos Content-Type. El navegador pondrá form-data con el boundary correcto.
        } else {
            config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
            config.body = JSON.stringify(data);
        }
    }

    // 4. Implementación de Timeout usando Abort Controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    config.signal = controller.signal;

    let response;
    try {
        response = await fetch(url, config);
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new TimeoutError(`La petición superó el tiempo máximo de ${timeout}ms.`);
        }
        throw new NetworkError('Problema de red. Servidor inalcanzable o error de conexión.');
    } finally {
        clearTimeout(timeoutId);
    }

    // 5. Manejo seguro del estado 401 (Refresh y Retry sin Loops)
    if (response.status === 401 && requiresAuth) {
        if (!_isRetry) {
            // Protección de Concurrencia para no gastar múltiples refresh
            if (!refreshPromise) {
                refreshPromise = refreshAccessToken().finally(() => {
                    refreshPromise = null;
                });
            }
            
            const refreshed = await refreshPromise;
            
            if (refreshed) {
                // Reintento de la petición original pasandole bandera de Retry
                return request(endpoint, { ...options, _isRetry: true });
            }
        }
        
        // 6. Centralizar Redirects usando Eventos
        storage.clear();
        emitAuthChanged();
        window.dispatchEvent(new CustomEvent(AUTH_EXPIRED_EVENT));
        throw new ApiError('Sesión ha expirado. Por favor, inicia sesión nuevamente.', 401, null);
    }

    // 6.b Manejo del estado 403 (Prohibido - Falta de Roles/Permisos)
    if (response.status === 403 && requiresAuth) {
        // A diferencia del 401, aquí NO cerramos sesión porque el token es válido,
        // simplemente el usuario no tiene los permisos o roles necesarios.
        window.dispatchEvent(new CustomEvent(AUTH_FORBIDDEN_EVENT));
        throw new ForbiddenError('No tienes los permisos o roles necesarios para realizar esta acción.', null);
    }

    // 7. Parseo Distinguido de Errores con Data del Backend
    if (!response.ok) {
        let errorData = null;
        let errorMessage = `HTTP Error ${response.status}`;
        try {
            errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            const text = await response.text();
            if (text) errorMessage = text;
        }
        throw new ApiError(errorMessage, response.status, errorData);
    }

    // Si todo va bien (204 = sin contenido)
    if (response.status === 204) return null;

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) return response.json();
    return response.text();
}

// ─── Auth Service ──────────────────────────────────────────────

export const authService = {

    async register(nombre, correoElectronico, password, organizationId = 1) {
        let data

        if (USE_MOCK) {
            data = await mockAuth.register(nombre, correoElectronico, password, organizationId)
        } else {
            data = await request('/auth/register', {
                method: 'POST',
                data: {
                    nombre,
                    correo_electronico: correoElectronico,
                    password,
                    organization_id: organizationId,
                },
            })
        }

        if (data.user_id) {
            storage.setUser(data)
            emitAuthChanged()
        }

        return data
    },

    async login(correoElectronico, password) {
        let data

        if (USE_MOCK) {
            data = await mockAuth.login(correoElectronico, password)
        } else {
            data = await request('/auth/login', {
                method: 'POST',
                data: {
                    correo_electronico: correoElectronico,
                    password,
                },
            })
        }

        storage.setTokens(data.access_token)

        const user = await this.me(data.access_token)
        storage.setUser(user)
        emitAuthChanged()
        return data
    },

    async me(accessToken = null) {
        const originalToken = storage.getAccessToken()
        if (accessToken && accessToken !== originalToken) {
            storage.setTokens(accessToken)
        }

        try {
            return await request('/auth/me', {
                method: 'GET',
                requiresAuth: true,
            })
        } finally {
            if (accessToken && accessToken !== originalToken) {
                if (originalToken) {
                    storage.setTokens(originalToken)
                }
            }
        }
    },

    logout() {
        storage.clear()
        emitAuthChanged()
        window.history.pushState({}, '', '/')
        window.dispatchEvent(new PopStateEvent('popstate'))
    },
}

// ─── Aplicacion Service ──────────────────────────────────────────────

export const aplicacionService = {
    async getAplicaciones() {
        return await request('/aplicaciones', { method: 'GET', requiresAuth: true });
    },
    async createAplicacion(data) {
        return await request('/aplicaciones', { method: 'POST', data, requiresAuth: true });
    }
};

// ─── PQRS Service ──────────────────────────────────────────────

export const pqrsService = {
    async submitPqrs(formData) {
        if (USE_MOCK) {
            return await mockPqrs.submit(formData);
        } else {
            // Utilizamos el request remozado que maneja FormData nativamente
            return await request('/pqrs', {
                method: 'POST',
                data: formData
                // requiresAuth: true // Descomentar si el backend requiere estar logueado para radicar PQRS no anónimas
            });
        }
    }
}

// ─── Chatbot Service ───────────────────────────────────────────

export const chatbotService = {
    async sendMessage(message) {
        if (USE_MOCK) {
            return await mockChatbot.sendMessage(message);
        } else {
            // Se envía como JSON
            const response = await request('/chatbot/message', {
                method: 'POST',
                data: { message }
            });
            // Asumiendo que el backend devuelve { "response": "string" } o directamente el string
            return response;
        }
    }
}

// ─── Aplicación Dashboard & PQRS Services ────────────────────────
export const dashboardService = {
    async getStats() {
        if (USE_MOCK) {
            // Simulated numbers for MVP
            return Promise.resolve({ active: 5, pending: 2 });
        }
        return request('/pqrs/dashboard', { method: 'GET', requiresAuth: true });
    }
};

export const pqrsListService = {
    async listActive() {
        if (USE_MOCK) {
            return mockPqrs.listActive();
        }
        return request('/pqrs/active', { method: 'GET', requiresAuth: true });
    },
    async getDetail(id) {
        if (USE_MOCK) {
            return mockPqrs.getDetail(id);
        }
        return request(`/pqrs/${id}`, { method: 'GET', requiresAuth: true });
    }
};

// Exported helpers used by aplicacion page
export const getDashboardData = dashboardService.getStats;
export const getActivePqrs = pqrsListService.listActive;
export const getPqrDetails = pqrsListService.getDetail;