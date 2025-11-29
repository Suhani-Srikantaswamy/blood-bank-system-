// Blood Network System JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // City-based hospital filtering
    const citySelect = document.getElementById('city');
    const hospitalSelect = document.getElementById('hospital_id');
    
    if (citySelect && hospitalSelect) {
        citySelect.addEventListener('change', function() {
            const selectedCity = this.value;
            
            if (selectedCity) {
                fetch(`/api/hospitals/${selectedCity}`)
                    .then(response => response.json())
                    .then(hospitals => {
                        hospitalSelect.innerHTML = '<option value="">Select Hospital</option>';
                        hospitals.forEach(hospital => {
                            const option = document.createElement('option');
                            option.value = hospital.hospital_id;
                            option.textContent = hospital.hospital_name;
                            hospitalSelect.appendChild(option);
                        });
                        hospitalSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching hospitals:', error);
                        hospitalSelect.innerHTML = '<option value="">Error loading hospitals</option>';
                    });
            } else {
                hospitalSelect.innerHTML = '<option value="">Select City First</option>';
                hospitalSelect.disabled = true;
            }
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Age validation for donors
    const ageInput = document.getElementById('age');
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            const age = parseInt(this.value);
            const feedback = this.nextElementSibling;
            
            if (age < 18 || age > 65) {
                this.setCustomValidity('Age must be between 18 and 65 years');
                if (feedback) {
                    feedback.textContent = 'Age must be between 18 and 65 years';
                }
            } else {
                this.setCustomValidity('');
                if (feedback) {
                    feedback.textContent = '';
                }
            }
        });
    }

    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const phone = this.value.replace(/\D/g, '');
            if (phone.length === 10) {
                this.setCustomValidity('');
            } else {
                this.setCustomValidity('Please enter a valid 10-digit phone number');
            }
        });
    });

    // Date validation for appointments
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateTimeInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const now = new Date();
            const maxDate = new Date();
            maxDate.setDate(maxDate.getDate() + 30);
            
            if (selectedDate < now) {
                this.setCustomValidity('Please select a future date and time');
            } else if (selectedDate > maxDate) {
                this.setCustomValidity('Appointments can only be booked up to 30 days in advance');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Confirm dialogs for critical actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-refresh dashboard data every 30 seconds
    if (document.querySelector('.dashboard')) {
        setInterval(function() {
            const dashboardCards = document.querySelectorAll('.stat-card');
            dashboardCards.forEach(function(card) {
                card.style.opacity = '0.8';
                setTimeout(function() {
                    card.style.opacity = '1';
                }, 500);
            });
        }, 30000);
    }

    // Blood availability checker
    const hospitalNetworkTable = document.getElementById('networkTable');
    if (hospitalNetworkTable) {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Search hospitals or blood groups...';
        
        hospitalNetworkTable.parentNode.insertBefore(searchInput, hospitalNetworkTable);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = hospitalNetworkTable.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Urgency level styling
    const urgencyBadges = document.querySelectorAll('.urgency-badge');
    urgencyBadges.forEach(function(badge) {
        const urgency = badge.textContent.toLowerCase();
        badge.classList.add(`urgency-${urgency}`);
    });

    // Real-time clock for dashboard
    function updateClock() {
        const clockElement = document.getElementById('current-time');
        if (clockElement) {
            const now = new Date();
            const timeString = now.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            clockElement.textContent = timeString;
        }
    }
    
    // Update clock every second
    setInterval(updateClock, 1000);
    updateClock(); // Initial call

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="loading"></span> Processing...';
                this.disabled = true;
            }
        });
    });

    // Blood group compatibility checker
    const bloodCompatibility = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    };

    // Add compatibility info to blood group displays
    const bloodGroupElements = document.querySelectorAll('.blood-group');
    bloodGroupElements.forEach(function(element) {
        const bloodGroup = element.textContent.trim();
        if (bloodCompatibility[bloodGroup]) {
            element.setAttribute('data-bs-toggle', 'tooltip');
            element.setAttribute('data-bs-placement', 'top');
            element.setAttribute('title', `Can donate to: ${bloodCompatibility[bloodGroup].join(', ')}`);
        }
    });

    // Emergency request priority handling
    const emergencyForms = document.querySelectorAll('.emergency-form');
    emergencyForms.forEach(function(form) {
        const urgencySelect = form.querySelector('select[name="urgency"]');
        if (urgencySelect) {
            urgencySelect.addEventListener('change', function() {
                const urgency = this.value;
                const submitButton = form.querySelector('button[type="submit"]');
                
                if (urgency === 'Critical') {
                    submitButton.classList.remove('btn-primary');
                    submitButton.classList.add('btn-danger');
                    submitButton.textContent = 'URGENT REQUEST';
                } else {
                    submitButton.classList.remove('btn-danger');
                    submitButton.classList.add('btn-primary');
                    submitButton.textContent = 'Submit Request';
                }
            });
        }
    });

    // Auto-save form data to localStorage
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(function(input) {
        // Load saved data
        const savedValue = localStorage.getItem(`form_${input.name}`);
        if (savedValue && input.type !== 'password') {
            input.value = savedValue;
        }
        
        // Save data on change
        input.addEventListener('change', function() {
            if (this.type !== 'password') {
                localStorage.setItem(`form_${this.name}`, this.value);
            }
        });
    });

    // Clear saved form data on successful submission
    const forms2 = document.querySelectorAll('form');
    forms2.forEach(function(form) {
        form.addEventListener('submit', function() {
            if (this.checkValidity()) {
                const inputs = this.querySelectorAll('input, select, textarea');
                inputs.forEach(function(input) {
                    localStorage.removeItem(`form_${input.name}`);
                });
            }
        });
    });

    console.log('Blood Network System initialized successfully!');
});