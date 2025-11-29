// Blood Bank System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Donor selection auto-fill blood group
    const donorSelect = document.getElementById('donor_id');
    const bloodGroupSelect = document.getElementById('blood_group');
    
    if (donorSelect && bloodGroupSelect) {
        donorSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.text.includes('(') && selectedOption.text.includes(')')) {
                const bloodGroup = selectedOption.text.match(/\(([^)]+)\)/)[1];
                bloodGroupSelect.value = bloodGroup;
            }
        });
    }

    // Confirmation for critical actions
    const approveButtons = document.querySelectorAll('a[href*="approve_request"]');
    const rejectButtons = document.querySelectorAll('a[href*="reject_request"]');
    
    approveButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to approve this emergency request?')) {
                e.preventDefault();
            }
        });
    });
    
    rejectButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to reject this emergency request?')) {
                e.preventDefault();
            }
        });
    });

    // Set today's date as default for collection date
    const collectionDateInput = document.getElementById('collected_on');
    if (collectionDateInput) {
        const today = new Date().toISOString().split('T')[0];
        collectionDateInput.value = today;
    }
});