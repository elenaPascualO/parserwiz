// DataToolkit Frontend Application

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

// Conversion options per file type
const CONVERSION_OPTIONS = {
    json: ['CSV', 'Excel'],
    csv: ['JSON'],
    xlsx: ['JSON'],
    xls: ['JSON']
}

// Current file reference
let currentFile = null

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
async function processFile(file) {
    currentFile = file
    showLoading()
    hideError()

    try {
        const formData = new FormData()
        formData.append('file', file)

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
        showError(error.message)
        resetUI()
    } finally {
        hideLoading()
    }
}

// Show preview section with data
function showPreview(file, data) {
    // Update file info
    fileName.textContent = file.name
    fileType.textContent = data.detected_type.toUpperCase()

    // Update row count
    const previewCount = data.rows.length
    rowCount.textContent = `Showing ${previewCount} of ${data.total_rows} rows`

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

    // Show preview section, hide upload section
    uploadSection.classList.add('hidden')
    previewSection.classList.remove('hidden')
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
            const match = disposition.match(/filename="(.+)"/)
            if (match) {
                downloadName = match[1]
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
    uploadSection.classList.remove('hidden')
    previewSection.classList.add('hidden')
    hideError()
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

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init)
