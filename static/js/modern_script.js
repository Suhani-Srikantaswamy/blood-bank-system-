// Blood Bank Management System - Modern JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAlerts();
    initializeFormValidation();
    initializeTableFeatures();
    initializeAnimations();
    initializeTooltips();
});

// Auto-hide alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            }
        }, 5000);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Add shake animation to invalid form
                form.classList.add('shake');
                setTimeout(() => form.classList.remove('shake'), 500);
            } else {
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                    
                    // Re-enable after 3 seconds (fallback)
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }, 3000);
                }
            }
            form.classList.add('was-validated');
        });
    });
}

// Table enhancements
function initializeTableFeatures() {
    // Add row click effects
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            // Remove active class from other rows
            tableRows.forEach(r => r.classList.remove('table-active'));
            // Add active class to clicked row
            this.classList.add('table-active');
        });
    });
    
    // Add search functionality to tables
    addTableSearch();
}

// Add search functionality to tables
function addTableSearch() {
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        const tableContainer = table.closest('.card');
        if (tableContainer && table.rows.length > 1) {
            addSearchBox(tableContainer, table);
        }
    });
}

function addSearchBox(container, table) {
    const cardHeader = container.querySelector('.card-header');
    if (cardHeader && !cardHeader.querySelector('.table-search')) {
        const searchHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">${cardHeader.innerHTML}</h5>
                <div class="table-search">
                    <input type="text" class="form-control form-control-sm" 
                           placeholder="Search..." style="width: 200px;">
                </div>
            </div>
        `;
        cardHeader.innerHTML = searchHTML;
        
        const searchInput = cardHeader.querySelector('input');
        searchInput.addEventListener('keyup', function() {
            filterTable(table, this.value);
        });
    }
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
            row.classList.add('fade-in');
        } else {
            row.style.display = 'none';
            row.classList.remove('fade-in');
        }
    });
}

// Initialize animations
function initializeAnimations() {
    // Add entrance animations to cards
    const cards = document.querySelectorAll('.card, .stat-card');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    });
    
    cards.forEach(function(card) {
        observer.observe(card);
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(function(btn) {
        btn.addEventListener('mouseenter', function() {
            this.classList.add('btn-hover');
        });
        
        btn.addEventListener('mouseleave', function() {
            this.classList.remove('btn-hover');
        });
    });
}

// Initialize tooltips
function initializeTooltips() {
    // Add tooltips to badges and icons
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(function(element) {
        new bootstrap.Tooltip(element);
    });
}

// Donor selection auto-fill blood group
function setupDonorBloodGroupSync() {
    const donorSelect = document.getElementById('donor_id');
    const bloodGroupSelect = document.getElementById('blood_group');
    
    if (donorSelect && bloodGroupSelect) {
        donorSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.text.includes('(') && selectedOption.text.includes(')')) {
                const bloodGroup = selectedOption.text.match(/\(([^)]+)\)/)[1];
                bloodGroupSelect.value = bloodGroup;
                
                // Add visual feedback
                bloodGroupSelect.classList.add('field-updated');
                setTimeout(() => bloodGroupSelect.classList.remove('field-updated'), 1000);
            }
        });
    }
}

// Confirmation dialogs for critical actions
function initializeConfirmations() {
    const criticalButtons = document.querySelectorAll('[data-confirm]');
    criticalButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// Real-time form validation feedback
function addRealTimeValidation() {
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Add custom validation messages
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!isValid && !feedback) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'invalid-feedback';
        feedbackDiv.textContent = field.validationMessage;
        field.parentNode.appendChild(feedbackDiv);
    }
}

// Dashboard auto-refresh
function initializeDashboardRefresh() {
    if (window.location.pathname.includes('dashboard')) {
        setInterval(function() {
            // Only refresh if user is active (not idle)
            if (document.hasFocus()) {
                updateDashboardStats();
            }
        }, 30000); // 30 seconds
    }
}

function updateDashboardStats() {
    // Fetch updated stats via AJAX (if endpoint exists)
    fetch('/api/dashboard-stats')
        .then(response => response.json())
        .then(data => {
            updateStatCards(data);
        })
        .catch(error => {
            console.log('Dashboard auto-refresh not available');
        });
}

function updateStatCards(data) {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(function(element, index) {
        if (data[index] !== undefined) {
            animateNumber(element, parseInt(element.textContent), data[index]);
        }
    });
}

function animateNumber(element, start, end) {
    const duration = 1000;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Initialize all features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupDonorBloodGroupSync();
    initializeConfirmations();
    addRealTimeValidation();
    initializeDashboardRefresh();
});

// Add CSS classes for animations
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        animation: slideInUp 0.6s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .field-updated {
        animation: fieldUpdate 1s ease-out;
    }
    
    @keyframes fieldUpdate {
        0% { background-color: rgba(40, 167, 69, 0.2); }
        100% { background-color: transparent; }
    }
    
    .btn-hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .table-active {
        background-color: rgba(220, 38, 38, 0.1) !important;
    }
`;
document.head.appendChild(style);