// ParserWiz Frontend Application

const API_BASE = '/api'

// DOM Elements
const uploadSection = document.getElementById('upload-section')
const previewSection = document.getElementById('preview-section')
const dropZone = document.getElementById('drop-zone')
const fileInput = document.getElementById('file-input')
const fileName = document.getElementById('file-name')
const fileType = document.getElementById('file-type')
const rowCount = document.getElementById('row-count')
const tableHead = document.getElementById('table-head')
const tableBody = document.getElementById('table-body')
const convertButtons = document.getElementById('convert-buttons')
const resetButton = document.getElementById('reset-button')
const loadingOverlay = document.getElementById('loading')
const errorMessage = document.getElementById('error-message')
const prevPageBtn = document.getElementById('prev-page')
const nextPageBtn = document.getElementById('next-page')
const pageInfo = document.getElementById('page-info')

// Editor elements
const editorSection = document.getElementById('editor-section')
const editorFileName = document.getElementById('editor-file-name')
const editorFileType = document.getElementById('editor-file-type')
const editorErrorText = document.getElementById('editor-error-text')
const rawEditor = document.getElementById('raw-editor')
const lineNumbers = document.getElementById('line-numbers')
const retryParseButton = document.getElementById('retry-parse-button')
const editorResetButton = document.getElementById('editor-reset-button')

// Export mode elements
const exportModeSection = document.getElementById('export-mode-section')
const complexityInfo = document.getElementById('complexity-info')
const proceedExportModeBtn = document.getElementById('proceed-export-mode')
const cancelExportModeBtn = document.getElementById('cancel-export-mode')

// Preview mode toggle elements
const previewModeToggle = document.getElementById('preview-mode-toggle')
const btnMultiFile = document.getElementById('btn-multi-file')
const btnSingleFile = document.getElementById('btn-single-file')
const multiTableAccordion = document.getElementById('multi-table-accordion')
const tableContainer = document.querySelector('.table-container')
const paginationControls = document.querySelector('.pagination-controls')

// Conversion options per file type
const CONVERSION_OPTIONS = {
    json: ['CSV', 'Excel'],
    csv: ['JSON', 'Excel'],
    xlsx: ['JSON', 'CSV'],
    xls: ['JSON', 'CSV']
}

// Current file reference
let currentFile = null

// Pagination state
let currentPage = 1
let totalPages = 1
let pageSize = 500
let cachedColumns = []
let cachedDetectedType = null

// Export mode state
let selectedExportMode = 'normal'
let jsonAnalysis = null

// Complex JSON preview state
let isComplexJson = false
let currentPreviewMode = 'multi' // 'multi' or 'single'
let multiTablePreviewData = null
let singleFilePreviewData = null

// Initialize event listeners
function init() {
    // Drag and drop events
    dropZone.addEventListener('dragover', handleDragOver)
    dropZone.addEventListener('dragleave', handleDragLeave)
    dropZone.addEventListener('drop', handleDrop)
    dropZone.addEventListener('click', () => fileInput.click())

    // File input change
    fileInput.addEventListener('change', handleFileSelect)

    // Reset button
    resetButton.addEventListener('click', resetUI)

    // Pagination buttons
    prevPageBtn.addEventListener('click', () => goToPage(currentPage - 1))
    nextPageBtn.addEventListener('click', () => goToPage(currentPage + 1))

    // Editor buttons
    retryParseButton.addEventListener('click', retryParse)
    editorResetButton.addEventListener('click', resetUI)

    // Sync line numbers with editor scroll
    rawEditor.addEventListener('scroll', syncLineNumbersScroll)
    rawEditor.addEventListener('input', updateLineNumbers)

    // Export mode buttons
    proceedExportModeBtn.addEventListener('click', proceedWithExportMode)
    cancelExportModeBtn.addEventListener('click', resetUI)

    // Preview mode toggle (for complex JSON)
    btnMultiFile.addEventListener('click', () => setPreviewMode('multi'))
    btnSingleFile.addEventListener('click', () => setPreviewMode('single'))
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault()
    e.stopPropagation()
    dropZone.classList.add('drag-over')
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault()
    e.stopPropagation()
    dropZone.classList.remove('drag-over')
}

// Handle file drop
function handleDrop(e) {
    e.preventDefault()
    e.stopPropagation()
    dropZone.classList.remove('drag-over')

    const files = e.dataTransfer.files
    if (files.length > 0) {
        processFile(files[0])
    }
}

// Handle file select from input
function handleFileSelect(e) {
    const files = e.target.files
    if (files.length > 0) {
        processFile(files[0])
    }
}

// Process uploaded file
async function processFile(file, page = 1) {
    currentFile = file
    currentPage = page
    showLoading()
    hideError()

    try {
        const extension = file.name.split('.').pop().toLowerCase()

        // For JSON files on first page, check complexity first
        if (page === 1 && extension === 'json' && selectedExportMode === 'normal') {
            const analysis = await analyzeJson(file)
            if (analysis.is_complex) {
                hideLoading()
                showExportModeChoice(analysis)
                return
            }
        }

        const formData = new FormData()
        formData.append('file', file)
        formData.append('page', page)
        formData.append('page_size', pageSize)
        formData.append('export_mode', selectedExportMode)

        const response = await fetch(`${API_BASE}/preview`, {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to preview file')
        }

        const data = await response.json()
        showPreview(file, data)
    } catch (error) {
        // Check if this is a parseable file type (JSON or CSV) on first page
        const extension = file.name.split('.').pop().toLowerCase()
        const isEditableType = ['json', 'csv'].includes(extension)

        if (page === 1 && isEditableType) {
            // Show raw editor for JSON/CSV parse errors
            await showRawEditor(file, error.message)
        } else if (page === 1) {
            resetUI()
            showError(error.message)
        } else {
            showError(error.message)
        }
    } finally {
        hideLoading()
    }
}

// Go to specific page
async function goToPage(page) {
    if (!currentFile || page < 1 || page > totalPages) return
    await processFile(currentFile, page)
}

// Show preview section with data
function showPreview(file, data) {
    // Update file info
    fileName.textContent = file.name
    fileType.textContent = data.detected_type.toUpperCase()

    // Update pagination state
    currentPage = data.current_page || 1
    totalPages = data.total_pages || 1
    cachedColumns = data.columns
    cachedDetectedType = data.detected_type

    // Update row count with range info
    const startRow = (currentPage - 1) * pageSize + 1
    const endRow = Math.min(startRow + data.rows.length - 1, data.total_rows)
    rowCount.textContent = `Showing ${startRow}-${endRow} of ${data.total_rows} rows`

    // Update pagination controls
    updatePaginationControls()

    // Build table header
    tableHead.innerHTML = ''
    const headerRow = document.createElement('tr')
    data.columns.forEach(col => {
        const th = document.createElement('th')
        th.textContent = col
        headerRow.appendChild(th)
    })
    tableHead.appendChild(headerRow)

    // Build table body
    tableBody.innerHTML = ''
    data.rows.forEach(row => {
        const tr = document.createElement('tr')
        row.forEach(cell => {
            const td = document.createElement('td')
            td.textContent = formatCellValue(cell)
            td.title = formatCellValue(cell) // Show full value on hover
            tr.appendChild(td)
        })
        tableBody.appendChild(tr)
    })

    // Build convert buttons
    buildConvertButtons(data.detected_type)

    // Show preview section, hide other sections
    uploadSection.classList.add('hidden')
    editorSection.classList.add('hidden')
    previewSection.classList.remove('hidden')

    // Scroll table to top
    const tableContainer = document.querySelector('.table-container')
    if (tableContainer) {
        tableContainer.scrollTop = 0
    }
}

// Update pagination controls state
function updatePaginationControls() {
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`
    prevPageBtn.disabled = currentPage <= 1
    nextPageBtn.disabled = currentPage >= totalPages
}

// Format cell value for display
function formatCellValue(value) {
    if (value === null || value === undefined) {
        return ''
    }
    if (typeof value === 'object') {
        return JSON.stringify(value)
    }
    return String(value)
}

// Build convert buttons based on file type
function buildConvertButtons(detectedType) {
    convertButtons.innerHTML = ''
    const options = CONVERSION_OPTIONS[detectedType] || []

    options.forEach(format => {
        const button = document.createElement('button')
        button.className = 'convert-btn'
        button.textContent = `Download as ${format}`
        button.addEventListener('click', () => convertFile(format.toLowerCase()))
        convertButtons.appendChild(button)
    })
}

// Convert file to specified format
async function convertFile(format) {
    if (!currentFile) return

    showLoading()
    hideError()

    // Map display format to API format
    const formatMap = {
        'csv': 'csv',
        'excel': 'xlsx',
        'json': 'json'
    }
    const outputFormat = formatMap[format] || format

    try {
        const formData = new FormData()
        formData.append('file', currentFile)
        formData.append('output_format', outputFormat)
        formData.append('export_mode', selectedExportMode)

        const response = await fetch(`${API_BASE}/convert`, {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to convert file')
        }

        // Get filename from Content-Disposition header
        const disposition = response.headers.get('Content-Disposition')
        let downloadName = `converted.${outputFormat}`
        if (disposition) {
            // Handle both filename="name" and filename*=UTF-8''name formats
            const match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/)
            if (match) {
                downloadName = decodeURIComponent(match[1])
            }
        }

        // Download the file
        const blob = await response.blob()
        downloadBlob(blob, downloadName)
    } catch (error) {
        showError(error.message)
    } finally {
        hideLoading()
    }
}

// Download blob as file
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}

// Reset UI to initial state
function resetUI() {
    currentFile = null
    fileInput.value = ''
    currentPage = 1
    totalPages = 1
    cachedColumns = []
    cachedDetectedType = null
    selectedExportMode = 'normal'
    jsonAnalysis = null

    // Reset complex JSON preview state
    isComplexJson = false
    currentPreviewMode = 'multi'
    multiTablePreviewData = null
    singleFilePreviewData = null

    // Hide all sections and show upload
    uploadSection.classList.remove('hidden')
    previewSection.classList.add('hidden')
    editorSection.classList.add('hidden')
    exportModeSection.classList.add('hidden')

    // Reset preview mode toggle and accordion
    previewModeToggle.classList.add('hidden')
    multiTableAccordion.classList.add('hidden')
    multiTableAccordion.innerHTML = ''
    tableContainer.classList.remove('hidden')
    paginationControls.classList.remove('hidden')

    // Reset mode toggle buttons
    btnMultiFile.classList.add('active')
    btnSingleFile.classList.remove('active')

    hideError()
}

// Show raw editor for malformed files
async function showRawEditor(file, errorMessage) {
    try {
        const content = await readFileAsText(file)
        const extension = file.name.split('.').pop().toLowerCase()

        // Update editor UI
        editorFileName.textContent = file.name
        editorFileType.textContent = extension.toUpperCase()
        editorErrorText.textContent = errorMessage
        rawEditor.value = content

        // Update line numbers
        updateLineNumbers()

        // Show editor section, hide others
        uploadSection.classList.add('hidden')
        previewSection.classList.add('hidden')
        editorSection.classList.remove('hidden')
    } catch (err) {
        // Fallback if file can't be read
        resetUI()
        showError(errorMessage)
    }
}

// Read file content as text
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = () => reject(new Error('Failed to read file'))
        reader.readAsText(file)
    })
}

// Update line numbers in editor
function updateLineNumbers() {
    const lines = rawEditor.value.split('\n')
    const numbers = lines.map((_, i) => i + 1).join('\n')
    lineNumbers.textContent = numbers
}

// Sync line numbers scroll with editor
function syncLineNumbersScroll() {
    lineNumbers.scrollTop = rawEditor.scrollTop
}

// Retry parsing with edited content
async function retryParse() {
    const content = rawEditor.value
    const extension = currentFile.name.split('.').pop().toLowerCase()

    // Determine MIME type
    const mimeTypes = {
        json: 'application/json',
        csv: 'text/csv'
    }
    const mimeType = mimeTypes[extension] || 'text/plain'

    // Create new file from edited content
    const editedFile = new File([content], currentFile.name, { type: mimeType })

    // Update current file reference and retry
    currentFile = editedFile
    await processFile(editedFile, 1)
}

// Analyze JSON file for complexity
async function analyzeJson(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: formData
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to analyze file')
    }

    return await response.json()
}

// Show export mode info for complex JSON
function showExportModeChoice(analysis) {
    jsonAnalysis = analysis

    // Build info text
    const arraysText = analysis.arrays_found
        .map(a => `${a.path} (${a.count} items)`)
        .join(', ')
    complexityInfo.innerHTML = `Found ${analysis.arrays_found.length} arrays that would expand to <strong>${analysis.estimated_rows.toLocaleString()} rows</strong>: ${arraysText}.<br><small>Formula: ${analysis.expansion_formula}</small>`

    // Show export mode section, hide others
    uploadSection.classList.add('hidden')
    previewSection.classList.add('hidden')
    editorSection.classList.add('hidden')
    exportModeSection.classList.remove('hidden')
}

// Proceed with selected export mode
async function proceedWithExportMode() {
    exportModeSection.classList.add('hidden')
    showLoading()

    try {
        // Fetch both previews in parallel for complex JSON
        const [multiTableData, singleFileData] = await Promise.all([
            fetchMultiTablePreview(currentFile),
            fetchSingleFilePreview(currentFile)
        ])

        multiTablePreviewData = multiTableData
        singleFilePreviewData = singleFileData

        hideLoading()
        showComplexJsonPreview(currentFile, multiTableData, singleFileData)
    } catch (error) {
        hideLoading()
        showError(error.message)
    }
}

// Fetch multi-table preview from API
async function fetchMultiTablePreview(file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('rows_per_table', 5)

    const response = await fetch(`${API_BASE}/preview-all-tables`, {
        method: 'POST',
        body: formData
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to fetch multi-table preview')
    }

    return await response.json()
}

// Fetch single-file preview from API (using single_row mode)
async function fetchSingleFilePreview(file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('page', 1)
    formData.append('page_size', 5)
    formData.append('export_mode', 'single_row')

    const response = await fetch(`${API_BASE}/preview`, {
        method: 'POST',
        body: formData
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to fetch single-file preview')
    }

    return await response.json()
}

// Show complex JSON preview with mode toggle
function showComplexJsonPreview(file, multiData, singleData) {
    isComplexJson = true
    currentPreviewMode = 'multi'
    selectedExportMode = 'multi_table'

    // Update file info
    fileName.textContent = file.name
    fileType.textContent = 'JSON'
    cachedDetectedType = 'json'

    // Show mode toggle
    previewModeToggle.classList.remove('hidden')

    // Render multi-table accordion
    renderMultiTableAccordion(multiData.tables)

    // Store single-file data for toggle
    singleFilePreviewData = singleData

    // Calculate total rows for multi-table
    const totalMultiRows = Object.values(multiData.tables).reduce((sum, t) => sum + t.total_rows, 0)
    rowCount.textContent = `${Object.keys(multiData.tables).length} tables, ${totalMultiRows} total rows`

    // Build convert buttons
    buildConvertButtons('json')

    // Show preview section with multi-file mode
    uploadSection.classList.add('hidden')
    editorSection.classList.add('hidden')
    previewSection.classList.remove('hidden')

    // Set initial view to multi-file
    setPreviewMode('multi')
}

// Render multi-table accordion
function renderMultiTableAccordion(tables) {
    multiTableAccordion.innerHTML = ''

    // Sort tables: 'main' first, then others alphabetically
    const tableNames = Object.keys(tables).sort((a, b) => {
        if (a === 'main') return -1
        if (b === 'main') return 1
        return a.localeCompare(b)
    })

    tableNames.forEach((tableName, index) => {
        const tableData = tables[tableName]
        const item = document.createElement('div')
        item.className = 'accordion-item'

        item.innerHTML = `
            <div class="accordion-header">
                <div class="accordion-header-left">
                    <span class="table-name">${tableName}</span>
                    <span class="row-count">${tableData.total_rows} rows</span>
                </div>
                <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="accordion-content">
                ${renderAccordionTable(tableData.columns, tableData.rows)}
            </div>
        `

        // Accordion toggle
        item.querySelector('.accordion-header').addEventListener('click', () => {
            item.classList.toggle('expanded')
        })

        multiTableAccordion.appendChild(item)
    })
}

// Render table HTML for accordion content
function renderAccordionTable(columns, rows) {
    let html = '<table><thead><tr>'
    columns.forEach(col => {
        html += `<th>${col}</th>`
    })
    html += '</tr></thead><tbody>'

    rows.forEach(row => {
        html += '<tr>'
        row.forEach(cell => {
            const value = formatCellValue(cell)
            html += `<td title="${value}">${value}</td>`
        })
        html += '</tr>'
    })

    if (rows.length === 0) {
        html += `<tr><td colspan="${columns.length}" style="text-align:center;color:var(--text-muted)">No data</td></tr>`
    }

    html += '</tbody></table>'
    return html
}

// Toggle preview mode between multi and single
function setPreviewMode(mode) {
    currentPreviewMode = mode

    // Update button states
    btnMultiFile.classList.toggle('active', mode === 'multi')
    btnSingleFile.classList.toggle('active', mode === 'single')

    // Update selectedExportMode for download
    selectedExportMode = mode === 'multi' ? 'multi_table' : 'single_row'

    if (mode === 'multi') {
        // Show accordion, hide table
        multiTableAccordion.classList.remove('hidden')
        tableContainer.classList.add('hidden')
        paginationControls.classList.add('hidden')

        // Update row count for multi-table
        if (multiTablePreviewData) {
            const totalRows = Object.values(multiTablePreviewData.tables).reduce((sum, t) => sum + t.total_rows, 0)
            rowCount.textContent = `${Object.keys(multiTablePreviewData.tables).length} tables, ${totalRows} total rows`
        }
    } else {
        // Show table, hide accordion
        multiTableAccordion.classList.add('hidden')
        tableContainer.classList.remove('hidden')
        paginationControls.classList.add('hidden') // Hide pagination for preview

        // Render single-file preview
        if (singleFilePreviewData) {
            renderSingleFilePreview(singleFilePreviewData)
        }
    }
}

// Render single-file preview table
function renderSingleFilePreview(data) {
    // Update row count
    rowCount.textContent = `${data.total_rows} rows (arrays as JSON text)`

    // Build table header
    tableHead.innerHTML = ''
    const headerRow = document.createElement('tr')
    data.columns.forEach(col => {
        const th = document.createElement('th')
        th.textContent = col
        headerRow.appendChild(th)
    })
    tableHead.appendChild(headerRow)

    // Build table body
    tableBody.innerHTML = ''
    data.rows.forEach(row => {
        const tr = document.createElement('tr')
        row.forEach(cell => {
            const td = document.createElement('td')
            td.textContent = formatCellValue(cell)
            td.title = formatCellValue(cell)
            tr.appendChild(td)
        })
        tableBody.appendChild(tr)
    })

    // Scroll to top
    if (tableContainer) {
        tableContainer.scrollTop = 0
    }
}

// Show loading overlay
function showLoading() {
    loadingOverlay.classList.remove('hidden')
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.add('hidden')
}

// Show error message
function showError(message) {
    errorMessage.textContent = message
    errorMessage.classList.remove('hidden')

    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError()
    }, 5000)
}

// Hide error message
function hideError() {
    errorMessage.classList.add('hidden')
}

// Feedback form elements (initialized in initFeedback)
let feedbackToggle
let feedbackFormContainer
let feedbackForm

// Initialize feedback form
function initFeedback() {
    feedbackToggle = document.getElementById('feedback-toggle')
    feedbackFormContainer = document.getElementById('feedback-form-container')
    feedbackForm = document.getElementById('feedback-form')

    if (!feedbackToggle || !feedbackFormContainer || !feedbackForm) {
        console.error('Feedback elements not found')
        return
    }

    feedbackToggle.addEventListener('click', () => {
        feedbackFormContainer.classList.toggle('hidden')
        feedbackToggle.textContent = feedbackFormContainer.classList.contains('hidden')
            ? 'Send Feedback'
            : 'Close'
    })

    feedbackForm.addEventListener('submit', handleFeedbackSubmit)
}

// Handle feedback form submission
async function handleFeedbackSubmit(e) {
    e.preventDefault()

    const form = e.target
    const submitBtn = form.querySelector('.feedback-submit')
    const emailInput = form.querySelector('#feedback-email')
    const messageInput = form.querySelector('#feedback-message')
    const originalText = submitBtn.textContent
    submitBtn.disabled = true
    submitBtn.textContent = 'Sending...'

    try {
        const response = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
                message: messageInput.value
            })
        })

        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to send feedback')
        }

        // Show success message
        feedbackFormContainer.innerHTML = '<p class="feedback-success">Thank you for your feedback!</p>'

        // Reset after 3 seconds
        setTimeout(() => {
            feedbackFormContainer.innerHTML = `
                <form id="feedback-form" class="feedback-form">
                    <input
                        type="email"
                        id="feedback-email"
                        placeholder="Email (optional)"
                        class="feedback-input"
                    >
                    <textarea
                        id="feedback-message"
                        placeholder="Your feedback..."
                        class="feedback-textarea"
                        required
                    ></textarea>
                    <button type="submit" class="feedback-submit">Send</button>
                </form>
            `
            feedbackFormContainer.classList.add('hidden')
            feedbackToggle.textContent = 'Send Feedback'
            // Re-attach event listener to new form
            document.getElementById('feedback-form').addEventListener('submit', handleFeedbackSubmit)
        }, 3000)
    } catch (error) {
        showError(error.message)
        submitBtn.disabled = false
        submitBtn.textContent = originalText
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    init()
    initFeedback()
})
