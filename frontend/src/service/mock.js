export const USE_MOCK = true;

// Simulador de retraso de red
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const mockAuth = {
    async register(nombre, correoElectronico, password, organizationId = 1) {
        await delay(800);
        return {
            user_id: 'mock-user-123',
            nombre,
            correo_electronico: correoElectronico,
            organization_id: organizationId,
        };
    },

    async login(correoElectronico, password) {
        await delay(800);
        if (correoElectronico === 'error') throw new Error('Credenciales inválidas simuladas');
        return {
            access_token: 'mock_access_token_123',
            token_type: 'bearer',
            user_id: 'mock-user-123',
            nombre: 'Usuario Mock',
            organization_id: 1,
        };
    }
};

export const mockPqrs = {
    // Submit a new PQRS (existing)
    async submit(formData) {
        await delay(1500); // Simulamos 1.5s de procesamiento (subida de archivos)
        if (formData.get('asunto') === 'error') {
            throw new Error('Error simulado al procesar la solicitud PQRS.');
        }
        const radicadoId = `RAD-${new Date().getFullYear()}-${Math.floor(100000 + Math.random() * 900000)}`;
        return { success: true, radicado: radicadoId, message: 'Solicitud radicada exitosamente' };
    },
    // Return a short list of active PQRS for sidebar
    async listActive() {
        await delay(500);
        // Simulated 10 active items
        return Array.from({ length: 10 }, (_, i) => ({
            id: i + 1,
            titulo: `PQRS #${i + 1}`
        }));
    },
    // Return detailed data for a given PQRS id
    async getDetail(id) {
        await delay(700);
        return {
            id,
            resumenIA: `Este es un resumen generado por IA para la PQRS ${id}.`,
            secretaria: 'Secretaría de Educación',
            secretariasCompetentes: ['Secretaría de Cultura', 'Secretaría de Salud'],
            descripcion: `Descripción completa de la PQRS ${id}. Aquí van los detalles que el usuario ingresó.`,
            adjuntos: [
                { name: 'documento.pdf', url: 'https://example.com/documento.pdf' },
                { name: 'foto.jpg', url: 'https://example.com/foto.jpg' }
            ]
        };
    },
    async checkExistsByRadicado(radicado) {
        await delay(400);
        const normalized = String(radicado || '').trim().toUpperCase();
        const found = TRACKING_MOCK_DB.find((item) => item.radicado === normalized);
        if (!found) {
            throw new Error('No encontramos una PQR con ese número de radicado.');
        }
        return { exists: true };
    },
    async getByRadicado(radicado) {
        await delay(650);
        const normalized = String(radicado || '').trim().toUpperCase();
        const found = TRACKING_MOCK_DB.find((item) => item.radicado === normalized);
        if (!found) {
            throw new Error('El radicado consultado no existe o no está disponible para consulta pública.');
        }
        return found;
    }
};

export const mockChatbot = {
    async sendMessage(message) {
        await delay(1200); // Simulamos "escribiendo..."

        // Simulación de error
        if (message.toLowerCase() === 'error') {
            throw new Error('Error de conexión simulado con el chatbot.');
        }

        return {
            success: true,
            response: "¡Hola! Entiendo lo que dices. Como asistente de la Alcaldía de Medellín, te sugiero que para radicar tu inquietud formalmente uses el botón 'Radicar PQR' aquí mismo en el portal."
        };
    }
};

const TRACKING_MOCK_DB = [
    {
        radicado: 'RAD-2026-123456',
        status: 'EN_GESTION',
        type: 'Petición',
        subject: 'Solicitud de información sobre programas de empleo juvenil',
        description: 'Solicito información sobre convocatorias abiertas de empleo y formación para jóvenes entre 18 y 28 años en Medellín.',
        created_at: '2026-04-10 09:35',
        channel: 'PORTAL',
        assigned_to: 'Secretaría de Desarrollo Económico',
        attachments: [
            { name: 'cedula.pdf' },
            { name: 'certificado_residencia.pdf' },
        ],
        response: null,
    },
    {
        radicado: 'RAD-2026-987654',
        status: 'RESPONDIDA',
        type: 'Reclamo',
        subject: 'Retraso en respuesta de trámite empresarial',
        description: 'Presento reclamo por retraso en la respuesta de mi trámite de fortalecimiento empresarial radicado anteriormente.',
        created_at: '2026-03-18 14:02',
        channel: 'WHATSAPP',
        assigned_to: 'Subsecretaría de Creación y Fortalecimiento Empresarial',
        attachments: [],
        response: {
            message: 'Se revisó su caso y se confirmó que el trámite quedó actualizado. A partir del 22 de abril puede continuar con la siguiente fase en ventanilla virtual.',
            responded_at: '2026-03-29 11:20',
        },
    },
];
