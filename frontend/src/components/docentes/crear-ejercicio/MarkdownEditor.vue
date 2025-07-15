<!-- src/components/docentes/crear-ejercicio/MarkdownEditor.vue -->
<template>
    <div class="markdown-form-group">
        <label class="form-label" for="description">
            <i class="icon-prefix">📖</i> Descripción
            <span class="markdown-badge">Markdown</span>
        </label>
        <div class="markdown-toolbar">
            <button type="button" class="toolbar-button" @click="insertMarkdown('bold')" title="Negrita">
                <i class="fas fa-bold"></i>
            </button>
            <button type="button" class="toolbar-button" @click="insertMarkdown('italic')" title="Cursiva">
                <i class="fas fa-italic"></i>
            </button>
            <button type="button" class="toolbar-button" @click="insertMarkdown('heading')" title="Encabezado">
                <i class="fas fa-heading"></i>
            </button>
            <button type="button" class="toolbar-button" @click="insertMarkdown('link')" title="Enlace">
                <i class="fas fa-link"></i>
            </button>
            <button type="button" class="toolbar-button" @click="insertMarkdown('code')" title="Código">
                <i class="fas fa-code"></i>
            </button>
            <button type="button" class="toolbar-button" @click="insertMarkdown('list')" title="Lista">
                <i class="fas fa-list-ul"></i>
            </button>
            <button type="button" class="toolbar-button" @click="openImageUploader" title="Imagen">
                <i class="fas fa-image"></i>
            </button>
            <button type="button" class="toolbar-button toolbar-button-right" @click="togglePreview"
                title="Alternar vista previa">
                <i :class="['fas', showPreview ? 'fa-eye-slash' : 'fa-eye']"></i>
            </button>
        </div>
        <div class="markdown-container" :class="{ 'full-width': !showPreview }">
            <div class="input-wrapper">
                <textarea ref="editorRef" class="markdown-textarea" id="description" :value="modelValue"
                    @input="$emit('update:modelValue', $event.target.value)" @scroll="debounceScroll"
                    placeholder="Explica tu desafío usando markdown. Puedes formatear texto, agregar código, imágenes y más."
                    rows="12"></textarea>
            </div>
            <div v-if="showPreview" class="preview-wrapper">
                <div ref="previewRef" class="markdown-preview" v-html="renderedMarkdown" @click="handlePreviewClick">
                </div>
                <span class="preview-label">Vista previa 👁️</span>
            </div>
        </div>

        <!-- Modal para guía de Markdown -->
        <div class="modal" :class="{ 'is-active': showMarkdownGuide }">
            <div class="modal-background" @click="showMarkdownGuide = false"></div>
            <div class="modal-card">
                <header class="modal-card-head">
                    <p class="modal-card-title">Guía de Markdown</p>
                    <button type="button" class="delete" aria-label="close" @click="showMarkdownGuide = false"></button>
                </header>
                <section class="modal-card-body">
                    <div class="markdown-guide">
                        <h3>Formato básico</h3>
                        <div class="guide-item">
                            <div class="guide-syntax">**texto**</div>
                            <div class="guide-result">Texto en <strong>negrita</strong></div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax">*texto*</div>
                            <div class="guide-result">Texto en <em>cursiva</em></div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax"># Título</div>
                            <div class="guide-result">Encabezado nivel 1</div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax">## Subtítulo</div>
                            <div class="guide-result">Encabezado nivel 2</div>
                        </div>

                        <h3>Enlaces e imágenes</h3>
                        <div class="guide-item">
                            <div class="guide-syntax">[texto del enlace](https://ejemplo.com)</div>
                            <div class="guide-result">Enlace a sitio web</div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax">![texto alternativo](URL de imagen)</div>
                            <div class="guide-result">Imagen desde URL</div>
                        </div>

                        <h3>Listas</h3>
                        <div class="guide-item">
                            <div class="guide-syntax">- Item 1<br>- Item 2<br>- Item 3</div>
                            <div class="guide-result">Lista con viñetas</div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax">1. Primer item<br>2. Segundo item<br>3. Tercer item</div>
                            <div class="guide-result">Lista numerada</div>
                        </div>

                        <h3>Código</h3>
                        <div class="guide-item">
                            <div class="guide-syntax">`código en línea`</div>
                            <div class="guide-result">Código dentro de un párrafo</div>
                        </div>
                        <div class="guide-item">
                            <div class="guide-syntax">```python<br>def hello_world():<br>&nbsp;&nbsp;print("Hola
                                mundo")<br>```</div>
                            <div class="guide-result">Bloque de código con resaltado de sintaxis</div>
                        </div>
                    </div>
                </section>
            </div>
        </div>

        <!-- Modal para subir imágenes -->
        <div class="modal" :class="{ 'is-active': showImageUploader }" ref="imageModal">
            <div class="modal-background" @click="showImageUploader = false"></div>
            <div class="modal-card" ref="imageModalCard">
                <header class="modal-card-head">
                    <p class="modal-card-title">Insertar imagen</p>
                    <button type="button" class="delete" aria-label="close" @click="showImageUploader = false"></button>
                </header>
                <section class="modal-card-body">
                    <div class="image-uploader">
                        <div class="tabs">
                            <ul>
                                <li :class="{ 'is-active': imageTab === 'upload' }" @click="imageTab = 'upload'">
                                    <a>Subir imagen</a>
                                </li>
                                <li :class="{ 'is-active': imageTab === 'url' }" @click="imageTab = 'url'">
                                    <a>Desde URL</a>
                                </li>
                                <li :class="{ 'is-active': imageTab === 'base64' }" @click="imageTab = 'base64'">
                                    <a>Embeber (Base64)</a>
                                </li>
                            </ul>
                        </div>

                        <div class="tab-content">
                            <!-- Subir imagen -->
                            <div v-if="imageTab === 'upload'" class="upload-tab">
                                <div class="file-upload-container">
                                    <div class="file-drop-area" :class="{ 'drag-over': isDragging }"
                                        @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false"
                                        @drop.prevent="handleFileDrop" @click="triggerFileInput">
                                        <p class="upload-text">
                                            <i class="fas fa-cloud-upload-alt"></i>
                                            Arrastra y suelta una imagen o haz clic para seleccionar
                                        </p>
                                        <input type="file" ref="fileInput" accept="image/*" class="file-input"
                                            @change="handleFileSelect" />
                                    </div>
                                    <div v-if="uploadError" class="upload-error">{{ uploadError }}</div>
                                    <div v-if="uploadedImage" class="upload-preview">
                                        <img :src="uploadedImage" alt="Vista previa" class="preview-image">
                                        <div class="image-details">
                                            <p>{{ uploadedFileName }} ({{ formatFileSize(uploadedFileSize) }})</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Imagen desde URL -->
                            <div v-if="imageTab === 'url'" class="url-tab">
                                <div class="field">
                                    <label class="label">URL de la imagen</label>
                                    <div class="control">
                                        <input type="text" class="input" v-model="imageUrl"
                                            placeholder="https://ejemplo.com/imagen.jpg">
                                    </div>
                                    <p class="help is-warning">
                                        Nota: las imágenes de URLs externas pueden dejar de funcionar si el sitio cambia
                                        o elimina la imagen.
                                    </p>
                                </div>
                                <div v-if="imageUrl" class="url-preview">
                                    <img :src="imageUrl" alt="Vista previa" class="preview-image">
                                </div>
                            </div>

                            <!-- Imagen Base64 -->
                            <div v-if="imageTab === 'base64'" class="base64-tab">
                                <div class="field">
                                    <label class="label">Insertar imagen como código Base64</label>
                                    <div class="control">
                                        <div class="file-upload-container">
                                            <div class="file-drop-area" :class="{ 'drag-over': isDragging }"
                                                @dragover.prevent="isDragging = true"
                                                @dragleave.prevent="isDragging = false"
                                                @drop.prevent="handleFileDropForBase64" @click="triggerBase64FileInput">
                                                <p class="upload-text">
                                                    <i class="fas fa-file-image"></i>
                                                    Arrastra y suelta una imagen para codificar en Base64
                                                </p>
                                                <input type="file" ref="base64FileInput" accept="image/*"
                                                    class="file-input" @change="handleFileSelectForBase64" />
                                            </div>
                                        </div>
                                        <p class="help">
                                            La imagen se codificará y guardará directamente en el markdown.
                                            Ideal para imágenes pequeñas (max. 500KB).
                                        </p>
                                    </div>
                                </div>
                                <div v-if="base64Image" class="base64-preview">
                                    <img :src="base64Image" alt="Vista previa Base64" class="preview-image">
                                    <div class="image-details">
                                        <p>Imagen codificada ({{ formatFileSize(base64Size) }})</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                <footer class="modal-card-foot">
                    <button type="button" class="button is-primary" @click.prevent="insertImage"
                        :disabled="!canInsertImage">
                        Insertar imagen
                    </button>
                    <button type="button" class="button" @click.prevent="showImageUploader = false">
                        Cancelar
                    </button>
                </footer>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

export default {
    name: 'MarkdownEditor',
    props: {
        modelValue: {
            type: String,
            default: ''
        }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
        // Refs para editor y vista previa
        const editorRef = ref(null);
        const previewRef = ref(null);
        const imageModal = ref(null);
        const imageModalCard = ref(null);

        // Estado de la vista previa
        const showPreview = ref(true);

        // Control de modal de guía
        const showMarkdownGuide = ref(false);

        // Variables para sincronización de scroll
        let isScrolling = false;
        let scrollRAF = null;
        let resizeObserver = null;
        let lastScrollTop = 0;
        let debounceTimer = null;

        // Modales y estado para imágenes
        const showImageUploader = ref(false);
        const imageTab = ref('upload');
        const isDragging = ref(false);
        const uploadedImage = ref(null);
        const uploadedFileName = ref('');
        const uploadedFileSize = ref(0);
        const uploadError = ref('');
        const imageUrl = ref('');
        const base64Image = ref('');
        const base64Size = ref(0);
        const fileInput = ref(null);
        const base64FileInput = ref(null);

        // Observar cuando se abre el modal para enfocar
        watch(showImageUploader, (newValue) => {
            if (newValue) {
                // Enfocar el modal cuando se abre
                nextTick(() => {
                    if (imageModalCard.value) {
                        // Asegurar que el modal esté en el viewport
                        imageModalCard.value.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        // Enfocar el primer input según la pestaña activa
                        if (imageTab.value === 'url' && imageUrl) {
                            const urlInput = document.querySelector('.url-tab .input');
                            if (urlInput) urlInput.focus();
                        }
                    }
                });
            }
        });

        // Caché para renderings anteriores de markdown
        const markdownCache = new Map();

        // Función para asegurar que el valor sea un string
        const ensureString = (value) => {
            if (value === null || value === undefined) return '';
            return String(value);
        };

        // Configurar Marked con resaltado de sintaxis
        const configureMarked = () => {
            // Definir un renderer personalizado
            const renderer = new marked.Renderer();

            // Personalizar cómo se renderizan los enlaces
            renderer.link = function ({ href, title, text }) {
                const safeHref = href || '#';
                const titleAttr = title ? ` title="${title}"` : '';
                return `<a href="${safeHref}"${titleAttr} target="_blank" rel="noopener noreferrer">${text}</a>`;
            };

            // Configurar marked con nuestro renderer
            marked.use({
                renderer,
                gfm: true,
                breaks: true,
                headerIds: true,
                headerPrefix: 'heading-',
                langPrefix: 'language-'
            });
        };

        // Configuración de DOMPurify
        const configureDOMPurify = () => {
            DOMPurify.addHook('afterSanitizeAttributes', function (node) {
                if (node.tagName === 'A') {
                    node.setAttribute('target', '_blank');
                    node.setAttribute('rel', 'noopener noreferrer');
                    node.setAttribute('data-external', 'true');
                }
            });
        };

        // Función de renderizado de Markdown con caché
        const renderedMarkdown = computed(() => {
            try {
                const content = props.modelValue || '';
                if (!content) return '';

                // Configurar marked cada vez
                configureMarked();

                // Renderizar el markdown directamente sin caché para depuración
                let html = marked.parse(content);

                // Sanitizar con opciones permisivas para enlaces
                html = DOMPurify.sanitize(html, {
                    ADD_TAGS: ['iframe'],
                    ADD_ATTR: ['allowfullscreen', 'frameborder', 'allow', 'src', 'data-external', 'target', 'rel', 'title', 'href'],
                    ALLOW_DATA_ATTR: true
                });

                return html;
            } catch (error) {
                console.error('Error al renderizar Markdown:', error);
                return `<p class="error">Error al renderizar el contenido: ${error.message}</p>`;
            }
        });

        // Controlador de scroll con debounce para mejor rendimiento
        const debounceScroll = (event) => {
            if (debounceTimer) {
                clearTimeout(debounceTimer);
            }

            // Solo ejecutamos si hay un cambio significativo en la posición del scroll
            const currentScrollTop = event.target.scrollTop;
            if (Math.abs(currentScrollTop - lastScrollTop) < 5) {
                return;
            }
            
            lastScrollTop = currentScrollTop;
            
            debounceTimer = setTimeout(() => {
                handleEditorScroll(event);
            }, 10); // Retraso pequeño para mejorar rendimiento
        };

        // Controlador de scroll mejorado
        const handleEditorScroll = (event) => {
            if (isScrolling || !showPreview.value) return;

            const editor = editorRef.value;
            const preview = previewRef.value;

            if (!editor || !preview) return;

            // Calcular la proporción de desplazamiento
            const scrollHeight = editor.scrollHeight - editor.clientHeight;
            const currentPosition = editor.scrollTop;

            if (scrollHeight <= 0) return;

            // Usar animationFrame para el scroll de la vista previa
            if (scrollRAF) {
                cancelAnimationFrame(scrollRAF);
            }

            scrollRAF = requestAnimationFrame(() => {
                isScrolling = true;
                const previewScrollHeight = preview.scrollHeight - preview.clientHeight;
                if (previewScrollHeight > 0) {
                    const scrollRatio = currentPosition / scrollHeight;
                    preview.scrollTop = scrollRatio * previewScrollHeight;
                }
                
                // Restablecer el bloqueo después de un breve retraso
                setTimeout(() => {
                    isScrolling = false;
                }, 100);
                
                scrollRAF = null;
            });
        };

        // Alternar vista previa
        const togglePreview = () => {
            showPreview.value = !showPreview.value;
            // Reajustar altura al cambiar la vista
            setTimeout(syncHeight, 0);
        };

        // Abrir guía de Markdown
        const openMarkdownGuide = () => {
            showMarkdownGuide.value = true;
        };

        // Insertar elementos Markdown en el textarea
        const insertMarkdown = (type) => {
            if (!editorRef.value) return;

            const textarea = editorRef.value;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = props.modelValue;
            const selectedText = text.substring(start, end);

            let insertion = '';
            let cursorOffset = 0;

            switch (type) {
                case 'bold':
                    insertion = `**${selectedText || 'texto en negrita'}**`;
                    cursorOffset = selectedText ? 0 : 2;
                    break;
                case 'italic':
                    insertion = `*${selectedText || 'texto en cursiva'}*`;
                    cursorOffset = selectedText ? 0 : 1;
                    break;
                case 'heading':
                    insertion = `## ${selectedText || 'Encabezado'}`;
                    cursorOffset = selectedText ? 0 : 11;
                    break;
                case 'link':
                    insertion = `[${selectedText || 'texto del enlace'}](https://www.ejemplo.com)`;
                    cursorOffset = selectedText ? 0 : 16;
                    break;
                case 'code':
                    if (selectedText.includes('\n')) {
                        insertion = `\`\`\`python\n${selectedText || 'def funcion():\n    pass'}\n\`\`\``;
                    } else {
                        insertion = `\`${selectedText || 'código'}\``;
                    }
                    cursorOffset = selectedText ? 0 : (insertion.includes('\n') ? 18 : 1);
                    break;
                case 'list':
                    insertion = `\n- ${selectedText || 'Elemento de lista'}\n- Segundo elemento\n- Tercer elemento`;
                    cursorOffset = selectedText ? 0 : 2;
                    break;
            }

            // Insertar en el texto
            const newText = text.substring(0, start) + insertion + text.substring(end);
            emit('update:modelValue', newText);

            // Restaurar la posición del cursor después de la actualización
            setTimeout(() => {
                textarea.focus();
                const newPosition = end + insertion.length - selectedText.length - cursorOffset;
                textarea.setSelectionRange(start, newPosition);
            }, 0);
        };

        // Abrir selector de imágenes
        const openImageUploader = () => {
            // Resetear estado de imágenes
            imageTab.value = 'upload';
            uploadedImage.value = null;
            uploadedFileName.value = '';
            uploadedFileSize.value = 0;
            uploadError.value = '';
            imageUrl.value = '';
            base64Image.value = '';
            base64Size.value = 0;

            showImageUploader.value = true;
        };
        
        // Activar el input de archivo al hacer clic en la zona de arrastre
        const triggerFileInput = () => {
            if (fileInput.value) {
                fileInput.value.click();
            }
        };
        
        // Activar el input de archivo base64 al hacer clic en la zona de arrastre
        const triggerBase64FileInput = () => {
            if (base64FileInput.value) {
                base64FileInput.value.click();
            }
        };

        // Manejar la selección de archivo
        const handleFileSelect = (event) => {
            handleFileUpload(event.target.files[0]);
        };

        // Manejar el arrastre y soltar
        const handleFileDrop = (event) => {
            isDragging.value = false;
            const file = event.dataTransfer.files[0];
            if (file) {
                handleFileUpload(file);
            }
        };

        // Procesar archivo subido
        const handleFileUpload = (file) => {
            if (!file) return;

            uploadError.value = '';

            // Verificar que sea una imagen
            if (!file.type.startsWith('image/')) {
                uploadError.value = 'El archivo debe ser una imagen';
                return;
            }

            // Verificar tamaño (máximo 5MB)
            if (file.size > 5 * 1024 * 1024) {
                uploadError.value = 'La imagen no debe superar los 5MB';
                return;
            }

            // Actualizar información del archivo
            uploadedFileName.value = file.name;
            uploadedFileSize.value = file.size;

            // Crear URL para vista previa
            uploadedImage.value = URL.createObjectURL(file);
        };

        // Manejar selección de archivo para Base64
        const handleFileSelectForBase64 = (event) => {
            handleFileUploadForBase64(event.target.files[0]);
        };

        // Manejar arrastre para Base64
        const handleFileDropForBase64 = (event) => {
            isDragging.value = false;
            const file = event.dataTransfer.files[0];
            if (file) {
                handleFileUploadForBase64(file);
            }
        };

        // Procesar archivo para Base64
        const handleFileUploadForBase64 = (file) => {
            if (!file) return;

            uploadError.value = '';

            // Verificar que sea una imagen
            if (!file.type.startsWith('image/')) {
                uploadError.value = 'El archivo debe ser una imagen';
                return;
            }

            // Verificar tamaño (máximo 500KB para base64)
            if (file.size > 500 * 1024) {
                uploadError.value = 'Para codificar en Base64, la imagen no debe superar los 500KB';
                return;
            }

            // Leer el archivo como Base64
            const reader = new FileReader();
            reader.onload = (e) => {
                base64Image.value = e.target.result;
                base64Size.value = file.size;
            };
            reader.readAsDataURL(file);
        };

        // Comprobar si se puede insertar una imagen
        const canInsertImage = computed(() => {
            if (imageTab.value === 'upload') return !!uploadedImage.value;
            if (imageTab.value === 'url') return !!imageUrl.value;
            if (imageTab.value === 'base64') return !!base64Image.value;
            return false;
        });

        // Insertar imagen en el markdown
        const insertImage = () => {
            if (!editorRef.value) return;

            const textarea = editorRef.value;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = props.modelValue;

            let imageMarkdown = '';

            if (imageTab.value === 'upload') {
                // Para una implementación real, aquí enviarías la imagen al servidor
                // y obtendrías la URL. Por ahora, usaremos un placeholder
                imageMarkdown = `![${uploadedFileName.value}](URL_AL_SUBIR_IMAGEN)`;
                alert('🚧 Sistema en desarrollo 🚧');
            } else if (imageTab.value === 'url') {
                imageMarkdown = `![Imagen](${imageUrl.value})`;
            } else if (imageTab.value === 'base64') {
                // Insertar imagen base64 directamente
                imageMarkdown = `![Imagen codificada](${base64Image.value})`;
            }

            // Insertar en el texto
            const newText = text.substring(0, start) + imageMarkdown + text.substring(end);
            emit('update:modelValue', newText);

            // Cerrar el modal
            showImageUploader.value = false;
        };

        // Formato de tamaño de archivo
        const formatFileSize = (bytes) => {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        };

        // Asegurar que editor y preview tengan la misma altura con mínimo re-renders
        const syncHeight = () => {
            if (!editorRef.value || !showPreview.value) return;
            
            const editor = editorRef.value;
            const preview = previewRef.value;
            
            if (!editor || !preview) return;
            
            // Establecer altura mínima si es necesario
            const minHeight = 300;
            // Usar la altura del contenido del editor como base
            const newHeight = Math.max(minHeight, editor.scrollHeight);
            
            // Aplicar la nueva altura solo si hay un cambio significativo
            // Esto reduce re-renders innecesarios
            if (Math.abs(parseInt(editor.style.height) - newHeight) > 10 || !editor.style.height) {
                editor.style.height = `${newHeight}px`;
                preview.style.height = `${newHeight}px`;
            }
        };

        // Observar cambios en el contenido para actualizar alturas con throttling
        let syncHeightTimer = null;
        watch(() => props.modelValue, () => {
            // Usar throttling para reducir actualizaciones frecuentes
            if (syncHeightTimer) {
                clearTimeout(syncHeightTimer);
            }
            syncHeightTimer = setTimeout(syncHeight, 300);
        });

        // Manejar clics en los enlaces de la vista previa
        const handlePreviewClick = (event) => {
            const anchor = event.target.closest('a');
            if (!anchor) return;

            event.preventDefault();
            event.stopPropagation();

            const href = anchor.getAttribute('href');
            if (href && href !== '#') {
                window.open(href, '_blank');
            }
        };

        // Configuración inicial
        onMounted(() => {
            // Configurar marked y DOMPurify
            configureMarked();
            configureDOMPurify();
            
            // Configurar sincronización inicial de alturas
            setTimeout(syncHeight, 100);
            
            // Virtual Scrolling: Uso de IntersectionObserver en lugar de ResizeObserver
            // para mejor rendimiento en la sincronización de altura
            if (window.IntersectionObserver && editorRef.value) {
                const observerOptions = {
                    root: null,
                    rootMargin: '0px',
                    threshold: [0, 0.5, 1]
                };
                
                const heightObserver = new IntersectionObserver((entries) => {
                    if (entries[0].isIntersecting) {
                        syncHeight();
                    }
                }, observerOptions);
                
                heightObserver.observe(editorRef.value);
                
                // Guardar referencia para limpiar después
                resizeObserver = heightObserver;
            } else if (window.ResizeObserver) {
                // Fallback a ResizeObserver
                resizeObserver = new ResizeObserver(syncHeight);
                if (editorRef.value) resizeObserver.observe(editorRef.value);
                if (previewRef.value) resizeObserver.observe(previewRef.value);
            } else {
                // Fallback para navegadores sin ResizeObserver
                window.addEventListener('resize', syncHeight);
            }
        });

        // Limpiar recursos
        onBeforeUnmount(() => {
            if (scrollRAF) {
                cancelAnimationFrame(scrollRAF);
            }
            
            if (resizeObserver) {
                resizeObserver.disconnect();
            }
            
            if (syncHeightTimer) {
                clearTimeout(syncHeightTimer);
            }
            
            if (debounceTimer) {
                clearTimeout(debounceTimer);
            }
            
            window.removeEventListener('resize', syncHeight);

            // Liberar URLs de objeto si existen
            if (uploadedImage.value) {
                URL.revokeObjectURL(uploadedImage.value);
            }
        });

        return {
            editorRef,
            previewRef,
            imageModal,
            imageModalCard,
            renderedMarkdown,
            handleEditorScroll,
            debounceScroll,
            togglePreview,
            showPreview,
            insertMarkdown,
            openMarkdownGuide,
            showMarkdownGuide,
            openImageUploader,
            showImageUploader,
            imageTab,
            isDragging,
            uploadedImage,
            uploadedFileName,
            uploadedFileSize,
            uploadError,
            imageUrl,
            base64Image,
            base64Size,
            fileInput,
            base64FileInput,
            handleFileSelect,
            handleFileDrop,
            handleFileSelectForBase64,
            handleFileDropForBase64,
            canInsertImage,
            insertImage,
            formatFileSize,
            triggerFileInput,
            triggerBase64FileInput,
            handlePreviewClick
        };
    }
}
</script>

<style>
/* =================== ESTILOS GLOBALES PARA MARKDOWN =================== */
.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4,
.markdown-preview h5,
.markdown-preview h6 {
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.markdown-preview h1 {
  font-size: 1.8rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.3rem;
}

.markdown-preview h2 {
  font-size: 1.5rem;
}

.markdown-preview h3 {
  font-size: 1.3rem;
}

.markdown-preview p {
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.markdown-preview strong {
  color: var(--color-text-primary);
  font-weight: 700;
}

.markdown-preview a {
  color: var(--color-info);
  text-decoration: none;
  border-bottom: 1px dotted var(--color-info);
  transition: all var(--transition-fast) ease;
  cursor: pointer;
}

.markdown-preview a:hover {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  text-decoration: none;
}

.markdown-preview a:focus {
  outline: 2px solid var(--color-secondary);
  outline-offset: 2px;
}

.markdown-preview ul,
.markdown-preview ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-preview ul li,
.markdown-preview ol li {
  margin-bottom: 0.5rem;
}

.markdown-preview blockquote {
  border-left: 4px solid var(--color-secondary);
  padding-left: 1rem;
  margin-left: 0;
  color: var(--color-text-secondary);
  font-style: italic;
}

.markdown-preview hr {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 1.5rem 0;
}

.markdown-preview img {
  max-width: 100%;
  border-radius: var(--border-radius);
  margin: 1rem 0;
}

.markdown-preview .video-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  margin: 1.5rem 0;
}

.markdown-preview .video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: var(--border-radius);
  border: none;
}

.markdown-preview code {
  background-color: var(--color-bg-element-alt);
  color: var(--color-accent-purple);
  padding: 0.2rem 0.4rem;
  border-radius: 0.3rem;
  font-family: 'Fira Code', 'Consolas', monospace;
  border: 1px solid var(--color-border);
}

.markdown-preview pre {
  margin: 1rem 0;
  border-radius: var(--border-radius);
  padding: 0;
  overflow: hidden;
}

.markdown-preview pre code {
  display: block;
  padding: 1rem;
  overflow-x: auto;
  border-radius: 0;
  background-color: var(--color-bg-darker);
  color: var(--color-text-primary);
  border: none;
}
</style>

<style scoped>
/* =================== CONTENEDOR PRINCIPAL =================== */
.markdown-form-group {
  margin-bottom: 1.5rem;
}

.markdown-badge {
  font-size: 0.7rem;
  background-color: var(--color-secondary);
  color: var(--color-text-primary);
  padding: 0.2rem 0.5rem;
  border-radius: 1rem;
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* =================== TOOLBAR =================== */
.markdown-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-bg-element);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  border: 1px solid var(--color-border);
  border-bottom: none;
}

.toolbar-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-bg-element-hover);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toolbar-button:hover {
  background-color: var(--color-secondary-dark);
  border-color: var(--color-secondary);
  color: var(--color-text-primary);
  transform: translateY(-1px);
}

.toolbar-button-right {
  margin-left: auto;
}

/* =================== CONTENEDOR MARKDOWN =================== */
.markdown-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  min-height: 300px;
  height: auto;
}

.markdown-container.full-width {
  grid-template-columns: 1fr;
}

.input-wrapper,
.preview-wrapper {
  display: flex;
  flex-direction: column;
  position: relative;
}

.preview-wrapper {
  transition: opacity var(--transition-fast);
}

/* =================== TEXTAREA =================== */
.markdown-textarea {
  min-height: 300px;
  height: 100%;
  overflow-y: auto;
  resize: vertical;
  padding: 0.75rem;
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: 0 0 var(--border-radius) var(--border-radius);
  color: var(--color-text-primary);
  font-size: 1rem;
  line-height: 1.5;
  font-family: 'Fira Code', 'Consolas', monospace;
  transition: all var(--transition-fast);
  width: 100%;
}

.markdown-textarea:focus {
  outline: none;
  border-color: var(--color-secondary);
  box-shadow: 0 0 0 2px rgba(138, 79, 255, 0.25);
}

/* =================== PREVIEW =================== */
.preview-label {
  position: absolute;
  top: -0.9rem;
  right: 1rem;
  background-color: var(--color-secondary);
  color: var(--color-text-primary);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  z-index: 5;
  font-weight: bold;
}

.markdown-preview {
  min-height: 300px;
  height: 100%;
  overflow-y: auto;
  background-color: var(--color-bg-element);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  color: var(--color-text-primary);
  line-height: 1.6;
}

/* =================== SUBIDA DE IMÁGENES =================== */
.image-uploader {
  padding: 1rem;
}

.file-upload-container {
  margin-bottom: 1rem;
}

.file-drop-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--border-radius);
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.file-drop-area:hover,
.file-drop-area.drag-over {
  border-color: var(--color-secondary);
  background-color: rgba(138, 79, 255, 0.05);
}

.upload-text {
  font-size: 1.1rem;
  color: var(--color-text-muted);
}

.upload-text i {
  display: block;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--color-secondary);
}

.file-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.upload-error {
  color: var(--color-coral);
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.upload-preview,
.url-preview,
.base64-preview {
  margin-top: 1rem;
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.image-details {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* =================== GUÍA DE MARKDOWN =================== */
.markdown-guide {
  padding: 1rem;
}

.guide-item {
  display: flex;
  margin-bottom: 0.8rem;
  gap: 1rem;
}

.guide-syntax {
  flex: 1;
  background-color: var(--color-bg-element);
  padding: 0.5rem;
  border-radius: var(--border-radius-sm);
  font-family: 'Fira Code', 'Consolas', monospace;
  color: var(--color-secondary-light);
}

.guide-result {
  flex: 1;
  padding: 0.5rem;
}

.video-error {
  background-color: var(--color-error-bg);
  border: 1px solid var(--color-error);
  color: var(--color-error);
  padding: 1rem;
  border-radius: var(--border-radius);
  margin: 1rem 0;
}

/* =================== MODAL =================== */
.modal-card-foot {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
}

.modal-card-foot .button {
  margin: 0;
  min-width: 120px;
  font-weight: 500;
}

.modal-card-foot .button.is-primary {
  background-color: var(--color-secondary);
}

.modal-card-foot .button.is-primary:hover {
  background-color: var(--color-secondary-light);
}

.modal-card-foot .button.is-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* =================== RESPONSIVE =================== */
@media (max-width: 768px) {
  .markdown-container {
    grid-template-columns: 1fr;
  }

  .markdown-container.full-width {
    grid-template-columns: 1fr;
  }

  .preview-wrapper {
    margin-top: 1rem;
  }

  .guide-item {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-card-foot {
    flex-direction: column;
    align-items: stretch;
  }
  
  .modal-card-foot .button {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}

@media (max-width: 480px) {
  .markdown-toolbar {
    justify-content: center;
  }
  
  .toolbar-button-right {
    margin-left: 0;
  }
}
</style>