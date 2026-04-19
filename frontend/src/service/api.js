import { storage } from './storage.js'

// Vite injects VITE_* env vars at build time. In dev this is undefined and we
// fall back to the local uvicorn. On Vercel, set VITE_API_BASE_URL on the
// project (e.g. https://<your-railway-app>.up.railway.app/api/v1).
export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
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
        const newAccessToken = tokenData.access_token || tokenData.accessToken || tokenData
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
        const data = await request('/auth/register', {
            method: 'POST',
            data: {
                nombre,
                correo_electronico: correoElectronico,
                password,
                organization_id: organizationId,
            },
        })

        if (data.user_id) {
            storage.setUser(data)
            emitAuthChanged()
        }

        return data
    },

    async login(correoElectronico, password) {
        const data = await request('/auth/login', {
            method: 'POST',
            data: {
                correo_electronico: correoElectronico,
                password,
            },
        })

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
        return await request('/pqrs', {
            method: 'POST',
            data: formData
        });
    }
}

// ─── PQRS Tracking Service (Consulta Ciudadana) ───────────────────
export const pqrsTrackingService = {
    /**
     * Validates if a radicado exists before navigating to detail view.
     *
     * Backend contract suggestion:
     * GET /pqrs/tracking/{radicado}/exists
     * -> { exists: boolean, message?: string }
     *
     * @param {string} radicado
     * @returns {Promise<{exists: boolean, message?: string}>}
     */
    async checkExists(radicado) {
        return await request(`/pqrs/track/${encodeURIComponent(radicado)}/exists`, {
            method: 'GET',
        });
    },

    async getByRadicado(radicado) {
        return await request(`/pqrs/track/${encodeURIComponent(radicado)}`, {
            method: 'GET',
        });
    },
}

// ─── Chatbot Flor Service (F7) ─────────────────────────────────

export const chatbotService = {
    /**
     * Envía una pregunta al chatbot Flor (anónimo).
     * @param {string} question
     * @returns {Promise<{answer: string, used_fallback: boolean, sources: {title: string, excerpt: string}[]}>}
     */
    async query(question) {
        return await request('/chatbot/query', {
            method: 'POST',
            data: { question },
            timeout: 30000, // generación LLM puede tardar unos segundos
        })
    },

    /**
     * Sube un documento (PDF o .md) a la base de conocimiento.
     * Requiere usuario autenticado.
     * @param {File} file
     * @returns {Promise<{chunks_indexed: number, source_path: string}>}
     */
    async uploadDocument(file) {
        const formData = new FormData()
        formData.append('file', file)
        return await request('/chatbot/documents', {
            method: 'POST',
            data: formData,
            requiresAuth: true,
            timeout: 120000, // PDFs grandes con OCR pueden tardar
        })
    },
}

// ─── Aplicación Dashboard & PQRS Services ────────────────────────
export const dashboardService = {
    async getStats() {
        return request('/pqrs/stats', { method: 'GET', requiresAuth: true });
    }
};

export const pqrsListService = {
    async listActive() {
        return request('/pqrs/curated', { method: 'GET', requiresAuth: true });
    },
    async getDetail(id) {
        return request(`/pqrs/curated/${id}`, { method: 'GET', requiresAuth: true });
    },
    async confirm(id, tipo) {
        return request(`/pqrs/curated/${id}`, {
            method: 'PATCH',
            requiresAuth: true,
            data: { tipo_confirmado: tipo, estado: 'PROCESANDO' }
        });
    },
    async sendResponse(id, texto) {
        return request(`/pqrs/curated/${id}/responder`, {
            method: 'POST',
            requiresAuth: true,
            data: { respuesta: texto }
        });
    },
    async getDraft(id) {
        return request(`/pqrs/curated/${id}/draft`, { method: 'GET', requiresAuth: true });
    },
    /**
     * F5 — Generates the 3-layer AI summary (lead, topics, original).
     * Persists under `resumen_ia` on the curated record.
     * @param {string} id radicado
     * @param {{force?: boolean}} opts
     */
    async summarize(id, { force = false } = {}) {
        const params = force ? { force: 'true' } : null;
        return request(`/pqrs/curated/${id}/summarize`, {
            method: 'POST',
            requiresAuth: true,
            params,
            timeout: 60000, // LLM calls
        });
    },
    /**
     * F5 — Generates a RAG-based draft response for the agent to review.
     * Persists under `borrador_respuesta` on the curated record.
     * @param {string} id radicado
     * @param {{force?: boolean}} opts
     */
    async draftResponse(id, { force = false } = {}) {
        const params = force ? { force: 'true' } : null;
        return request(`/pqrs/curated/${id}/draft-response`, {
            method: 'POST',
            requiresAuth: true,
            params,
            timeout: 90000, // LLM + RAG, longer reply
        });
    },
};

// ─── Mapa de Comunas (F6) ─────────────────────────────────────────
export const mapService = {
    /**
     * Devuelve la distribución de PQRS por comunas de Medellín con análisis IA.
     * @returns {Promise<{total_pqrs: number, total_mapped: number, communes: Array}>}
     */
    async getDensity() {
        return request('/pqrs/map', { method: 'GET', requiresAuth: true, timeout: 30000 });
    },
};

// Exported helpers used by aplicacion page
export const getDashboardData = dashboardService.getStats;
export const getActivePqrs = pqrsListService.listActive;
export const getPqrDetails = pqrsListService.getDetail;