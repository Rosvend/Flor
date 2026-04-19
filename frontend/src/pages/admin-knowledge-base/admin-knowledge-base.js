import '../../../assets/main.css'
import './admin-knowledge-base.css'
import { renderNavbar } from '../../components/navbar/navbar.js'
import { storage } from '../../service/storage.js'
import { chatbotService, ApiError, ForbiddenError } from '../../service/api.js'

export function renderAdminKnowledgeBase() {
    if (!storage.isAuthenticated()) {
        window.history.replaceState({}, '', '/login')
        window.dispatchEvent(new PopStateEvent('popstate'))
        return
    }

    const app = document.getElementById('app')
    app.innerHTML = `
        <a class="skip-link" href="#main-content">Saltar al contenido principal</a>
        ${renderNavbar({ currentPath: '/admin/knowledge-base' })}

        <main id="main-content" class="admin-kb-layout">
            <div class="admin-kb-card">
                <h1 class="admin-kb-title">Base de conocimiento de Flor</h1>
                <p class="admin-kb-subtitle">
                    Sube documentos PDF o Markdown para enriquecer las respuestas del
                    chatbot. Los textos se procesan, dividen en fragmentos e indexan
                    automáticamente. Sólo sube información de carácter público.
                </p>

                <form class="admin-kb-form" autocomplete="off">
                    <div class="admin-kb-file-row">
                        <label for="kb-file">Archivo (.pdf o .md, máx. 25 MB)</label>
                        <input
                            id="kb-file"
                            class="admin-kb-file-input"
                            type="file"
                            name="file"
                            accept=".pdf,.md,application/pdf,text/markdown"
                            required
                        />
                    </div>

                    <div class="admin-kb-actions">
                        <button type="submit" class="admin-kb-submit">Subir e indexar</button>
                    </div>

                    <div class="admin-kb-status" hidden></div>
                </form>

                <div class="admin-kb-help">
                    <strong>¿Qué pasa al subir un documento?</strong><br>
                    1. Si es PDF, se convierte a Markdown (con OCR si es escaneado).<br>
                    2. Se divide en fragmentos basados en encabezados.<br>
                    3. Cada fragmento se indexa con embeddings multilingües en Chroma.<br>
                    4. Flor podrá responder preguntas usando ese contenido inmediatamente.
                </div>
            </div>
        </main>
    `

    const form = app.querySelector('.admin-kb-form')
    const fileInput = app.querySelector('#kb-file')
    const submitBtn = app.querySelector('.admin-kb-submit')
    const statusEl = app.querySelector('.admin-kb-status')

    function showStatus(message, kind = 'info') {
        statusEl.hidden = false
        statusEl.className = `admin-kb-status admin-kb-status--${kind}`
        statusEl.textContent = message
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault()
        const file = fileInput.files?.[0]
        if (!file) return

        submitBtn.disabled = true
        showStatus(`Subiendo "${file.name}"… esto puede tardar varios segundos para PDFs escaneados.`, 'info')

        try {
            const result = await chatbotService.uploadDocument(file)
            showStatus(
                `✔ Indexados ${result.chunks_indexed} fragmentos del archivo "${file.name}".`,
                'ok'
            )
            form.reset()
        } catch (err) {
            if (err instanceof ForbiddenError) {
                showStatus('No tienes permiso para subir documentos.', 'error')
            } else if (err instanceof ApiError && err.status === 401) {
                showStatus('Tu sesión expiró. Vuelve a iniciar sesión.', 'error')
            } else if (err instanceof ApiError && err.status === 415) {
                showStatus(err.message || 'Tipo de archivo no soportado. Usa .pdf o .md.', 'error')
            } else if (err instanceof ApiError && err.status === 413) {
                showStatus('El archivo supera el tamaño máximo permitido (25 MB).', 'error')
            } else {
                showStatus(err?.message || 'No pudimos indexar el documento.', 'error')
            }
        } finally {
            submitBtn.disabled = false
        }
    })
}
