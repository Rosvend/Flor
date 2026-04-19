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
    async submit(formData) {
        await delay(1500); // Simulamos 1.5s de procesamiento (subida de archivos)

        // Simulación de error (puedes probar enviando asunto="error" para verlo)
        if (formData.get('asunto') === 'error') {
            throw new Error('Error simulado al procesar la solicitud PQRS.');
        }

        // Generar un número de radicado aleatorio
        const radicadoId = `RAD-${new Date().getFullYear()}-${Math.floor(100000 + Math.random() * 900000)}`;

        return {
            success: true,
            radicado: radicadoId,
            message: 'Solicitud radicada exitosamente'
        };
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
