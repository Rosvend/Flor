import '../../../assets/main.css';
import './pqrs.css';
import { renderNavbar } from '../../components/navbar/navbar.js';
import { pqrsService } from '../../service/api.js';

export function renderPqrs() {
    const app = document.getElementById('app');

    app.innerHTML = `
        <div class="mesh-bg" aria-hidden="true"></div>

        ${renderNavbar({ currentPath: '/pqrs' })}

        <main id="main-content" class="main-content pqrs-main">
            <div class="container pqrs-container">
                
                <!-- Pantalla de Éxito (Oculta por defecto) -->
                <div id="pqrs-success" class="card pqrs-success-card hidden">
                    <div class="success-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-success"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                    </div>
                    <h2 class="text-3xl mt-4" style="color: var(--color-tertiary);">¡Radicación Exitosa!</h2>
                    <p class="text-lg text-secondary mt-2">Su solicitud ha sido registrada correctamente en el sistema.</p>
                    
                    <div class="radicado-box mt-6">
                        <span class="text-sm text-secondary">Número de Radicado</span>
                        <h3 id="radicado-number" class="text-4xl mt-1" style="color: var(--color-primary);">RAD-0000</h3>
                        <p class="text-sm text-muted mt-2">Guarde este número para consultar el estado de su solicitud.</p>
                    </div>

                    <div class="mt-8">
                        <a href="/" class="btn btn--primary btn--lg" data-link>Volver al Inicio</a>
                    </div>
                </div>

                <!-- Formulario -->
                <div id="pqrs-form-container" class="card pqrs-card">
                    <div class="card__header">
                        <h1 class="card__title text-2xl">Formulario de Radicación de PQRS</h1>
                        <p class="text-secondary mt-1">Complete todos los campos requeridos para procesar su solicitud.</p>
                    </div>
                    
                    <form id="pqrs-form" class="pqrs-form">
                        
                        <!-- Toggle Anónimo -->
                        <div class="anonimo-toggle-wrapper mb-6">
                            <span class="text-sm font-semibold text-tertiary mr-3">Radicar como Anónimo</span>
                            <label class="switch">
                                <input type="checkbox" id="is-anonimo" name="is_anonimo">
                                <span class="slider round"></span>
                            </label>
                            <p class="text-xs text-muted mt-2">Si radica como anónimo, no le pediremos sus datos personales, pero debe proporcionar un correo para notificarle el resultado.</p>
                        </div>

                        <!-- Sección: Datos Personales (Se oculta si es anónimo) -->
                        <div id="section-personales" class="form-section">
                            <h3 class="section-title">1. Datos del Solicitante</h3>
                            <div class="grid-2-col">
                                <div class="form-group">
                                    <label for="persona" class="form-label form-label--required">Tipo de Persona</label>
                                    <select id="persona" name="persona" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="Natural">Natural</option>
                                        <option value="Juridica">Jurídica</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="tipo_doc" class="form-label form-label--required">Tipo de Documento</label>
                                    <select id="tipo_doc" name="tipo_documento" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="CC">Cédula de ciudadanía</option>
                                        <option value="CE">Cédula de extranjería</option>
                                        <option value="TI">Tarjeta de identidad</option>
                                        <option value="PA">Pasaporte</option>
                                        <option value="NIT">NIT</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="num_doc" class="form-label form-label--required">Número de Documento</label>
                                    <input type="number" id="num_doc" name="numero_documento" class="form-input" required>
                                </div>
                                <div class="form-group">
                                    <label id="lbl-nombres" for="nombres" class="form-label form-label--required">Nombres y apellidos</label>
                                    <input type="text" id="nombres" name="nombres" class="form-input" required>
                                </div>
                                <div class="form-group">
                                    <label for="genero" class="form-label form-label--required">Género</label>
                                    <select id="genero" name="genero" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="Masculino">Masculino</option>
                                        <option value="Femenino">Femenino</option>
                                        <option value="No binario">No binario</option>
                                        <option value="Prefiero no decirlo">Prefiero no decirlo</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Sección: Datos de Contacto -->
                        <div class="form-section">
                            <h3 class="section-title">2. Datos de Contacto</h3>
                            <div class="grid-2-col">
                                <div class="form-group">
                                    <label for="pais" class="form-label form-label--required">País</label>
                                    <select id="pais" name="pais" class="form-select" required>
                                        <option value="Colombia" selected>Colombia</option>
                                        <option value="Venezuela">Venezuela</option>
                                        <option value="Ecuador">Ecuador</option>
                                        <option value="Peru">Perú</option>
                                        <option value="Estados Unidos">Estados Unidos</option>
                                        <option value="España">España</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="form-group" id="depto-wrapper">
                                    <label for="departamento" class="form-label form-label--required">Departamento</label>
                                    <select id="departamento" name="departamento" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="Antioquia">Antioquia</option>
                                        <option value="Cundinamarca">Cundinamarca</option>
                                        <option value="Valle del Cauca">Valle del Cauca</option>
                                        <option value="Atlantico">Atlántico</option>
                                        <option value="Bolivar">Bolívar</option>
                                        <option value="Santander">Santander</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="ciudad" class="form-label form-label--required">Ciudad</label>
                                    <select id="ciudad" name="ciudad" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="Medellin">Medellín</option>
                                        <option value="Bello">Bello</option>
                                        <option value="Itagui">Itagüí</option>
                                        <option value="Envigado">Envigado</option>
                                        <option value="Sabaneta">Sabaneta</option>
                                        <option value="Rionegro">Rionegro</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="direccion" class="form-label form-label--required">Dirección</label>
                                    <input type="text" id="direccion" name="direccion" class="form-input" placeholder="Ej. Calle 10 #43A-12" required>
                                </div>
                                <div class="form-group">
                                    <label for="email" class="form-label form-label--required">Correo electrónico</label>
                                    <input type="email" id="email" name="email" class="form-input" placeholder="su@correo.com" required>
                                </div>
                                <div class="form-group">
                                    <label for="telefono" class="form-label">Teléfono (opcional)</label>
                                    <input type="number" id="telefono" name="telefono" class="form-input" placeholder="3001234567">
                                </div>
                            </div>
                        </div>

                        <!-- Sección: Detalles de la Solicitud -->
                        <div class="form-section">
                            <h3 class="section-title">3. Detalles de la Solicitud</h3>
                            <div class="grid-2-col">
                                <div class="form-group">
                                    <label for="asunto" class="form-label form-label--required">Asunto principal</label>
                                    <select id="asunto" name="asunto" class="form-select" required>
                                        <option value="" disabled selected>Seleccione...</option>
                                        <option value="Peticion">Petición</option>
                                        <option value="Queja">Queja</option>
                                        <option value="Reclamo">Reclamo</option>
                                        <option value="Sugerencia">Sugerencia</option>
                                        <option value="Felicitacion">Felicitación</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="atencion_pref" class="form-label form-label--required">Atención preferencial</label>
                                    <select id="atencion_pref" name="atencion_preferencial" class="form-select" required>
                                        <option value="Ninguna" selected>Ninguna</option>
                                        <option value="Adulto mayor">Adulto mayor</option>
                                        <option value="Persona con discapacidad">Persona con discapacidad</option>
                                        <option value="Mujer embarazada">Mujer embarazada</option>
                                        <option value="Victima de conflicto">Víctima de conflicto</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="dir_hecho" class="form-label form-label--required">Dirección del hecho</label>
                                    <select id="dir_hecho" name="direccion_hecho_tipo" class="form-select" required>
                                        <option value="Misma">Misma dirección de contacto</option>
                                        <option value="Otra">Otra dirección</option>
                                    </select>
                                </div>
                                <div class="form-group hidden" id="otra-dir-wrapper">
                                    <label for="otra_dir" class="form-label form-label--required">Especifique la dirección</label>
                                    <input type="text" id="otra_dir" name="otra_direccion" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label for="es_info" class="form-label form-label--required">¿Es una solicitud de información?</label>
                                    <select id="es_info" name="es_solicitud_informacion" class="form-select" required>
                                        <option value="No" selected>No</option>
                                        <option value="Si">Sí</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="autoriza_notif" class="form-label form-label--required">¿Autoriza notificación por correo?</label>
                                    <select id="autoriza_notif" name="autoriza_notificacion" class="form-select" required>
                                        <option value="Si" selected>Sí</option>
                                        <option value="No">No</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-group mt-4">
                                <label for="descripcion" class="form-label form-label--required">Descripción detallada</label>
                                <textarea id="descripcion" name="descripcion" class="form-textarea" placeholder="Describa los hechos de forma clara y concisa (mínimo 20 caracteres)..." minlength="20" required></textarea>
                                <div class="form-hint mt-1">Por favor sea lo más específico posible para facilitar la gestión.</div>
                            </div>
                        </div>

                        <!-- Sección: Anexos -->
                        <div class="form-section">
                            <h3 class="section-title">4. Documentos Anexos</h3>
                            <div class="form-group">
                                <label for="tiene_anexos" class="form-label form-label--required">¿Desea adjuntar archivos?</label>
                                <select id="tiene_anexos" name="tiene_anexos" class="form-select" required>
                                    <option value="No" selected>No</option>
                                    <option value="Si">Sí</option>
                                </select>
                            </div>
                            
                            <div id="anexos-wrapper" class="hidden mt-4">
                                <p class="text-sm text-secondary mb-3">Puede adjuntar hasta 5 archivos (PDF, JPG, PNG). Tamaño máximo: 5MB por archivo.</p>
                                <div class="grid-2-col">
                                    <div class="form-group">
                                        <label class="form-label">Archivo 1</label>
                                        <input type="file" name="archivo_1" accept=".pdf,.jpg,.jpeg,.png" class="form-input form-file">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Archivo 2</label>
                                        <input type="file" name="archivo_2" accept=".pdf,.jpg,.jpeg,.png" class="form-input form-file">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Archivo 3</label>
                                        <input type="file" name="archivo_3" accept=".pdf,.jpg,.jpeg,.png" class="form-input form-file">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Archivo 4</label>
                                        <input type="file" name="archivo_4" accept=".pdf,.jpg,.jpeg,.png" class="form-input form-file">
                                    </div>
                                    <div class="form-group">
                                        <label class="form-label">Archivo 5</label>
                                        <input type="file" name="archivo_5" accept=".pdf,.jpg,.jpeg,.png" class="form-input form-file">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Error Global -->
                        <div id="form-error" class="form-error-box hidden mt-4"></div>

                        <!-- Actions -->
                        <div class="form-actions mt-6" style="display: flex; gap: 15px; justify-content: flex-end;">
                            <a href="/" class="btn btn--ghost btn--lg" data-link>Cancelar</a>
                            <button type="submit" id="btn-submit" class="btn btn--primary btn--lg">
                                Radicar Solicitud
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </main>
    `;

    setupFormLogic();
}

function setupFormLogic() {
    const form = document.getElementById('pqrs-form');
    const toggleAnonimo = document.getElementById('is-anonimo');
    const secPersonales = document.getElementById('section-personales');
    
    // Selects
    const personaSelect = document.getElementById('persona');
    const paisSelect = document.getElementById('pais');
    const dirHechoSelect = document.getElementById('dir_hecho');
    const anexosSelect = document.getElementById('tiene_anexos');
    
    // Wrappers / Labels
    const lblNombres = document.getElementById('lbl-nombres');
    const deptoWrapper = document.getElementById('depto-wrapper');
    const deptoInput = document.getElementById('departamento');
    const otraDirWrapper = document.getElementById('otra-dir-wrapper');
    const otraDirInput = document.getElementById('otra_dir');
    const anexosWrapper = document.getElementById('anexos-wrapper');
    
    // Anónimo Toggle
    toggleAnonimo.addEventListener('change', (e) => {
        if (e.target.checked) {
            secPersonales.classList.add('hidden');
            // Quitar required de los inputs personales
            const inputs = secPersonales.querySelectorAll('input, select');
            inputs.forEach(i => i.required = false);
        } else {
            secPersonales.classList.remove('hidden');
            const inputs = secPersonales.querySelectorAll('input, select');
            inputs.forEach(i => i.required = true);
        }
    });

    // Persona Jurídica -> Razón Social
    personaSelect.addEventListener('change', (e) => {
        if (e.target.value === 'Juridica') {
            lblNombres.textContent = 'Razón social';
        } else {
            lblNombres.textContent = 'Nombres y apellidos';
        }
    });

    // País != Colombia -> Ocultar departamento
    paisSelect.addEventListener('change', (e) => {
        if (e.target.value !== 'Colombia') {
            deptoWrapper.classList.add('hidden');
            deptoInput.required = false;
        } else {
            deptoWrapper.classList.remove('hidden');
            deptoInput.required = true;
        }
    });

    // Otra dirección
    dirHechoSelect.addEventListener('change', (e) => {
        if (e.target.value === 'Otra') {
            otraDirWrapper.classList.remove('hidden');
            otraDirInput.required = true;
        } else {
            otraDirWrapper.classList.add('hidden');
            otraDirInput.required = false;
        }
    });

    // Anexos
    anexosSelect.addEventListener('change', (e) => {
        if (e.target.value === 'Si') {
            anexosWrapper.classList.remove('hidden');
        } else {
            anexosWrapper.classList.add('hidden');
            // Limpiar archivos si elige "No"
            const files = anexosWrapper.querySelectorAll('input[type="file"]');
            files.forEach(f => f.value = '');
        }
    });

    // Validar archivos peso
    const fileInputs = document.querySelectorAll('.form-file');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files[0] && this.files[0].size > 5 * 1024 * 1024) {
                alert('El archivo supera el límite de 5MB');
                this.value = ''; // Limpiar
            }
        });
    });

    // Validar teléfono (sólo ejemplo: max 10 dígitos)
    const telInput = document.getElementById('telefono');
    telInput.addEventListener('input', function() {
        if (this.value.length > 10) {
            this.value = this.value.slice(0, 10);
        }
    });

    // Submit form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btnSubmit = document.getElementById('btn-submit');
        const errorBox = document.getElementById('form-error');
        errorBox.classList.add('hidden');
        errorBox.textContent = '';
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = 'Procesando...';

        try {
            const formData = new FormData(form);
            
            // Asegurar que el estado del toggle vaya
            formData.set('es_anonimo', toggleAnonimo.checked ? 'true' : 'false');
            
            // Llamada al backend
            const response = await pqrsService.submitPqrs(formData);
            
            // Éxito: Ocultar form, mostrar pantalla de éxito
            document.getElementById('pqrs-form-container').classList.add('hidden');
            document.getElementById('pqrs-success').classList.remove('hidden');
            document.getElementById('radicado-number').textContent = response.radicado || response.data?.radicado;

        } catch (err) {
            errorBox.textContent = err.message || 'Ha ocurrido un error al radicar la solicitud.';
            errorBox.classList.remove('hidden');
            
            // Scroll to error
            errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Radicar Solicitud';
        }
    });
}
