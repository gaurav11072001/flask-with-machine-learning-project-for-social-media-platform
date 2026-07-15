// Admin Panel JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin panel
    initializeAdminPanel();
    
    // Auto-hide alerts after 5 seconds
    autoHideAlerts();
    
    // Initialize confirmation dialogs
    initializeConfirmations();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize search functionality
    initializeSearch();
});

/**
 * Initialize admin panel functionality
 */
function initializeAdminPanel() {
    console.log('Admin Panel initialized');
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Update active navigation
    updateActiveNavigation();
}

/**
 * Auto-hide alert messages after 5 seconds
 */
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Initialize confirmation dialogs for dangerous actions
 */
function initializeConfirmations() {
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    const flagButtons = document.querySelectorAll('[data-action="flag"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const itemType = this.dataset.itemType || 'item';
            const itemName = this.dataset.itemName || 'this item';
            
            if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
    
    flagButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.dataset.flagAction || 'flag';
            const itemName = this.dataset.itemName || 'this item';
            
            if (!confirm(`Are you sure you want to ${action} ${itemName}?`)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize search functionality with debouncing
 */
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"]');
    
    searchInputs.forEach(input => {
        let debounceTimer;
        
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                // Auto-submit search after 500ms of inactivity
                if (this.value.length >= 2 || this.value.length === 0) {
                    this.closest('form').submit();
                }
            }, 500);
        });
    });
}

/**
 * Update active navigation item based on current URL
 */
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Show loading state for elements
 */
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

/**
 * Hide loading state for elements
 */
function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

/**
 * Display admin notifications
 */
function showAdminNotification(message, type = 'info', duration = 3000) {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.alert-container') || document.querySelector('main');
    container.insertAdjacentHTML('afterbegin', alertHTML);
    
    // Auto-hide after duration
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, duration);
}

/**
 * AJAX helper function for admin operations
 */
function adminAjax(url, data = {}, method = 'POST') {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: method !== 'GET' ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Admin AJAX Error:', error);
        showAdminNotification('An error occurred. Please try again.', 'danger');
        throw error;
    });
}

/**
 * Get CSRF token for AJAX requests
 */
function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrf_token"]');
    return tokenInput ? tokenInput.value : '';
}

/**
 * Bulk action handler
 */
function handleBulkAction() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="bulk_select"]:checked');
    const actionSelect = document.querySelector('select[name="bulk_action"]');
    
    if (checkboxes.length === 0) {
        showAdminNotification('Please select items to perform bulk action.', 'warning');
        return false;
    }
    
    if (!actionSelect || !actionSelect.value) {
        showAdminNotification('Please select an action to perform.', 'warning');
        return false;
    }
    
    const action = actionSelect.value;
    const items = Array.from(checkboxes).map(cb => cb.value);
    
    if (confirm(`Are you sure you want to ${action} ${items.length} selected item(s)?`)) {
        // Perform bulk action
        return true;
    }
    
    return false;
}

/**
 * Toggle all checkboxes
 */
function toggleAllCheckboxes(masterCheckbox) {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="bulk_select"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = masterCheckbox.checked;
    });
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Initialize charts if Chart.js is available
 */
function initializeCharts() {
    if (typeof Chart === 'undefined') return;
    
    // Analytics charts
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    
    chartElements.forEach(canvas => {
        const chartType = canvas.dataset.chart;
        const chartData = JSON.parse(canvas.dataset.chartData || '{}');
        
        new Chart(canvas, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    });
}

/**
 * Real-time updates for dashboard
 */
function initializeRealTimeUpdates() {
    // Update dashboard stats every 30 seconds
    if (window.location.pathname.includes('/admin')) {
        setInterval(() => {
            updateDashboardStats();
        }, 30000);
    }
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats() {
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update stat cards
            Object.keys(data).forEach(key => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    element.textContent = formatNumber(data[key]);
                }
            });
        })
        .catch(error => {
            console.error('Failed to update stats:', error);
        });
}

/**
 * Export data functionality
 */
function exportData(format, endpoint) {
    showAdminNotification('Preparing export...', 'info');
    
    const url = `${endpoint}?format=${format}`;
    
    // Create hidden link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `export_${Date.now()}.${format}`;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showAdminNotification('Export completed!', 'success');
}

// Initialize real-time updates when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeRealTimeUpdates();
    initializeCharts();
});

// Keyboard shortcuts for admin
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Shift + A: Go to admin dashboard
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        window.location.href = '/admin';
    }
    
    // Escape: Close modals and dropdowns
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
        
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.previousElementSibling);
            if (bsDropdown) bsDropdown.hide();
        });
    }
});

// Handle browser back/forward buttons
window.addEventListener('popstate', function() {
    updateActiveNavigation();
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Admin Panel Error:', e.error);
    // Only show user-friendly errors in production
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        showAdminNotification('An unexpected error occurred.', 'danger');
    }
});
