// Main JavaScript for Screenshot News Analyzer
console.log('Screenshot News Analyzer - Web Interface Loaded');

// Global configuration
const API_BASE = '/api';
const POLL_INTERVAL = 2000; // 2 seconds

// Utility functions
function showNotification(message, type = 'info') {
    // TODO: Implement toast notifications
    console.log(`${type.toUpperCase()}: ${message}`);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!validTypes.includes(file.type)) {
        return { valid: false, error: 'Please select a valid image file (JPG, PNG, WEBP, BMP, TIFF)' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, error: 'File size must be less than 10MB' };
    }
    
    return { valid: true };
}

// API functions
window.uploadFile = async function(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        console.log('Making upload request to /api/upload...');
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('Upload response received:', response);
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Upload error response:', error);
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        console.log('Upload success response:', result);
        return result;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

window.checkJobStatus = async function(jobId) {
    try {
        const response = await fetch(`/api/status/${jobId}`);
        
        if (!response.ok) {
            throw new Error('Failed to check status');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Status check error:', error);
        throw error;
    }
}

window.getJobResults = async function(jobId) {
    try {
        const response = await fetch(`/api/results/${jobId}`);
        
        if (!response.ok) {
            throw new Error('Failed to get results');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Results error:', error);
        throw error;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
    // Add any global event listeners or initialization code here
    
    // Example: Add loading states
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.classList.add('loading');
            }
        });
    });
});