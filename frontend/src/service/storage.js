/* ================================================================
   STORAGE.JS — Wrapper de localStorage para autenticación
   ================================================================
   Centraliza todo acceso a localStorage en un único lugar.
   Si se cambia de localStorage a cookies o sessionStorage en el
   futuro, solo se edita este archivo — ningún otro cambia.

   Las claves (KEYS) tienen prefijo 'medemovil' para evitar
   colisiones con otras apps en el mismo dominio.
   ================================================================ */

const KEYS = {
    ACCESS_TOKEN:  'AccessToken',
    REFRESH_TOKEN: 'RefreshToken',
    USER:          'User',
}

export const storage = {

    /* ── ¿Está el usuario autenticado? ──
       Boolean simple: si hay un access token en storage → sí.
       No valida la firma del JWT (eso es trabajo del backend). */
    isAuthenticated() {
        return !!localStorage.getItem(KEYS.ACCESS_TOKEN)
    },

    /* ── Obtener tokens ── */
    getAccessToken()  { return localStorage.getItem(KEYS.ACCESS_TOKEN) },
    getRefreshToken() { return localStorage.getItem(KEYS.REFRESH_TOKEN) },

    /* ── Guardar tokens después de login/signup ──
       refreshToken es opcional (algunos backends no lo usan). */
    setTokens(accessToken, refreshToken = null) {
        localStorage.setItem(KEYS.ACCESS_TOKEN, accessToken)
        if (refreshToken) localStorage.setItem(KEYS.REFRESH_TOKEN, refreshToken)
    },

    /* ── Usuario ──
       Guardamos el objeto usuario para mostrar nombre, avatar, etc.
       getUser() parsea el JSON almacenado y devuelve el objeto. */
    getUser() {
        const raw = localStorage.getItem(KEYS.USER)
        try { return raw ? JSON.parse(raw) : null }
        catch { return null }
    },
    setUser(user) {
        localStorage.setItem(KEYS.USER, JSON.stringify(user))
    },

    /* ── Roles y Autorización ──
       Funciones para manejar permisos si el backend soporta múltiples tipos de usuario (ej. 'admin', 'user') */
    getRole() {
        const user = this.getUser()
        return user ? user.role : null // Ajustar 'role' según cómo lo envíe el backend
    },
    
    hasRole(requiredRole) {
        const role = this.getRole()
        if (!role) return false
        if (Array.isArray(role)) return role.includes(requiredRole)
        return role === requiredRole
    },

    /* ── Limpiar TODO al hacer logout ──
       Elimina cada clave individualmente (no usa localStorage.clear()
       para no borrar datos de otras apps en el mismo dominio). */
    clear() {
        Object.values(KEYS).forEach(key => localStorage.removeItem(key))
    },
}
