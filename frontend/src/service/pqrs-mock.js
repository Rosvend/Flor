/* ================================================================
   PQRS-MOCK.JS — Datos simulados para la página de gestión PQRS
   ================================================================
   Simula la respuesta del backend para la bandeja de PQRS y el
   detalle de cada solicitud. Al conectar con el backend real,
   sólo se reemplaza este archivo por llamadas a api.js.
   ================================================================ */

const delay = (ms = 400) => new Promise(resolve => setTimeout(resolve, ms));

// ── CATÁLOGO DE TIPOS ──────────────────────────────────────────────
export const TIPO_PQRS = {
    PETICION:   { label: 'Petición',   color: '#3b82f6', bg: '#eff6ff' },
    QUEJA:      { label: 'Queja',      color: '#ef4444', bg: '#fef2f2' },
    RECLAMO:    { label: 'Reclamo',    color: '#f97316', bg: '#fff7ed' },
    SUGERENCIA: { label: 'Sugerencia', color: '#22c55e', bg: '#f0fdf4' },
};

export const CANAL = {
    WEB:      'Canal Web',
    PRESENCIAL: 'Presencial',
    TELEFONO: 'Teléfono',
    APP:      'App Móvil',
};

// ── BANDEJA (lista de PQRs) ────────────────────────────────────────
const BANDEJA_MOCK = [
    {
        id: 'RAD-2026-04821',
        tipo: 'PETICION',
        canal: 'WEB',
        fechaRadicado: '2026-10-15',
        fechaVence: '2026-10-15', // hoy → "Vence Hoy"
        asunto: 'Solicitud de información sobre los requisitos para acceder a crédito de...',
        confianza: 95,
        estado: 'PENDIENTE',
    },
    {
        id: 'RAD-2026-04822',
        tipo: 'QUEJA',
        canal: 'PRESENCIAL',
        fechaRadicado: '2026-10-10',
        fechaVence: '2026-10-17', // 2 días
        asunto: 'Queja por mala atención en la sede administrativa del centro, el...',
        confianza: 88,
        estado: 'PENDIENTE',
    },
    {
        id: 'RAD-2026-04823',
        tipo: 'RECLAMO',
        canal: 'APP',
        fechaRadicado: '2026-10-08',
        fechaVence: '2026-10-20', // 5 días
        asunto: 'Reporte de un hueco peligroso en la avenida principal frente a la estación.',
        confianza: 92,
        estado: 'PENDIENTE',
    },
    {
        id: 'RAD-2026-04824',
        tipo: 'SUGERENCIA',
        canal: 'WEB',
        fechaRadicado: '2026-10-05',
        fechaVence: '2026-10-22', // 7 días
        asunto: 'Sugerencia para mejorar la iluminación del parque del barrio.',
        confianza: 75,
        estado: 'PENDIENTE',
    },
];

// ── DETALLE COMPLETO POR ID ────────────────────────────────────────
const DETALLE_MOCK = {
    'RAD-2026-04821': {
        id: 'RAD-2026-04821',
        tipo: 'PETICION',
        canal: 'WEB',
        fechaRadicado: '2026-10-15',
        fechaVence: '2026-10-15',
        asunto: 'Solicitud de información sobre requisitos para crédito de fomento',
        confianza: 95,
        estado: 'PENDIENTE',

        // Capas de análisis IA
        capas: {
            solicitudConcreta: 'El ciudadano solicita información detallada sobre los requisitos, tasas de interés y plazos para acceder a la línea de crédito de fomento para microempresarios, específicamente para el sector comercio.',
            tematicas: ['Crédito', 'Banco', 'Requisitos', 'Microempresario'],
            textoOriginal: '"Buenos días, señores. Les escribo porque tengo un pequeño negocio de abarrotes en el barrio Aranjuez y me comentaron que la alcaldía está ofreciendo unos créditos especiales para pequeños empresarios como yo. Quisiera saber cuáles son los documentos que necesito, cuánto tiempo me dan para pagar y cuáles son las tasas de interés que manejan. También quiero saber si hay alguna oficina donde me puedan atender personalmente para resolver mis dudas. Muchas gracias por su atención."',
        },

        // Panel derecho: precedente
        precedente: {
            id: 'RAD-2026-03102',
            resumen: 'Respuesta estándar aprobada sobre líneas de crédito "Medellín Adelante".',
            similitud: 95,
        },

        // Info adicional ciudadano
        infoCiudadano: {
            historialLimpio: true,
            solicitudesPrevias: 2,
        },
    },

    'RAD-2026-04822': {
        id: 'RAD-2026-04822',
        tipo: 'QUEJA',
        canal: 'PRESENCIAL',
        fechaRadicado: '2026-10-10',
        fechaVence: '2026-10-17',
        asunto: 'Mala atención en sede administrativa del centro',
        confianza: 88,
        estado: 'PENDIENTE',

        capas: {
            solicitudConcreta: 'El ciudadano reporta haber recibido un trato inadecuado por parte de un funcionario de la sede administrativa del centro de la ciudad, quien le negó información sobre su solicitud previa sin justificación válida.',
            tematicas: ['Atención al ciudadano', 'Funcionario', 'Sede Centro', 'Maltrato'],
            textoOriginal: '"Me dirijo a ustedes para manifestar mi inconformidad con el trato recibido el pasado martes en las instalaciones de la sede administrativa del centro. El señor que me atendió en la ventanilla 3 fue muy grosero y me dijo que volviera otro día sin explicarme por qué no podía atenderme. Llevo tres visitas intentando resolver un trámite de pensión y cada vez me dicen algo diferente. Espero que tomen las medidas necesarias."',
        },

        precedente: {
            id: 'RAD-2025-11203',
            resumen: 'Protocolo de respuesta para quejas de atención al ciudadano con compromiso de investigación interna.',
            similitud: 88,
        },

        infoCiudadano: {
            historialLimpio: false,
            solicitudesPrevias: 5,
        },
    },

    'RAD-2026-04823': {
        id: 'RAD-2026-04823',
        tipo: 'RECLAMO',
        canal: 'APP',
        fechaRadicado: '2026-10-08',
        fechaVence: '2026-10-20',
        asunto: 'Hueco peligroso en avenida principal frente a la estación',
        confianza: 92,
        estado: 'PENDIENTE',

        capas: {
            solicitudConcreta: 'El ciudadano reclama la reparación urgente de un hundimiento en el pavimento ubicado frente a la estación de metro La Floresta, el cual representa un riesgo para peatones y vehículos.',
            tematicas: ['Infraestructura vial', 'Seguridad', 'Pavimento', 'Estación Metro'],
            textoOriginal: '"Estimados señores de la alcaldía, les escribo para reclamar por el hueco que lleva más de dos meses en la avenida principal, justo frente a la estación La Floresta. Este hueco es muy grande y ya ha causado accidentes. La semana pasada vi cómo una motocicleta cayó ahí. Es urgente que lo reparen antes de que ocurra una tragedia. He llamado a la línea 311 pero nadie me da respuesta concreta."',
        },

        precedente: {
            id: 'RAD-2026-02847',
            resumen: 'Reclamo similar atendido con remisión a Secretaría de Infraestructura y cierre en 15 días hábiles.',
            similitud: 92,
        },

        infoCiudadano: {
            historialLimpio: true,
            solicitudesPrevias: 1,
        },
    },

    'RAD-2026-04824': {
        id: 'RAD-2026-04824',
        tipo: 'SUGERENCIA',
        canal: 'WEB',
        fechaRadicado: '2026-10-05',
        fechaVence: '2026-10-22',
        asunto: 'Mejora de iluminación en parque del barrio',
        confianza: 75,
        estado: 'PENDIENTE',

        capas: {
            solicitudConcreta: 'El ciudadano sugiere instalar luminarias adicionales en el parque del barrio Belén Rincón, específicamente en la zona de juegos infantiles y la cancha múltiple, para mejorar la seguridad nocturna.',
            tematicas: ['Alumbrado público', 'Parques', 'Seguridad', 'Belén Rincón'],
            textoOriginal: '"Buenas tardes. Quiero sugerir que pongan más luces en el parque del barrio Belén Rincón. La zona de los columpios y la cancha de microfútbol quedan muy oscuras en las noches y los jóvenes y niños no pueden jugar con tranquilidad. Además, ha habido algunos robos en esa área por falta de iluminación. Sería muy bueno que evaluaran la posibilidad de instalar paneles solares para el alumbrado del parque."',
        },

        precedente: {
            id: 'RAD-2025-09341',
            resumen: 'Sugerencia similar implementada en barrio Buenos Aires con instalación de 8 luminarias LED.',
            similitud: 75,
        },

        infoCiudadano: {
            historialLimpio: true,
            solicitudesPrevias: 0,
        },
    },
};

// ── API MOCK ───────────────────────────────────────────────────────

export const pqrsMockService = {
    /**
     * Obtiene la bandeja de PQRs pendientes.
     * @returns {Promise<{total: number, items: Array}>}
     */
    async getBandeja() {
        await delay(300);
        return {
            total: BANDEJA_MOCK.length,
            pendientes: BANDEJA_MOCK.filter(p => p.estado === 'PENDIENTE').length,
            items: BANDEJA_MOCK,
        };
    },

    /**
     * Obtiene el detalle completo de una PQR por su ID (radicado).
     * @param {string} id — e.g. "RAD-2026-04821"
     * @returns {Promise<Object>}
     */
    async getById(id) {
        await delay(400);
        const detalle = DETALLE_MOCK[id];
        if (!detalle) throw new Error(`PQR con ID "${id}" no encontrada.`);
        return detalle;
    },

    /**
     * Confirma la clasificación de una PQR (simula PATCH /pqrs/:id/clasificacion).
     * @param {string} id
     * @param {string} tipo — nuevo tipo si se reclasificó
     * @returns {Promise<{success: boolean}>}
     */
    async confirmarClasificacion(id, tipo) {
        await delay(600);
        return { success: true, message: `Clasificación de ${id} confirmada como ${tipo}.` };
    },

    /**
     * Envía la respuesta a una PQR (simula POST /pqrs/:id/respuesta).
     * @param {string} id
     * @param {string} texto
     * @returns {Promise<{success: boolean}>}
     */
    async enviarRespuesta(id, texto) {
        await delay(800);
        if (!texto.trim()) throw new Error('La respuesta no puede estar vacía.');
        return { success: true, message: `Respuesta enviada para ${id}.` };
    },
};
