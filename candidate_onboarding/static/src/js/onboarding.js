document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Initialize the onboarding form
    const onboardingForm = document.getElementById('onboarding_form');
    if (!onboardingForm) return;

    // File validation
    function validateFiles(form) {
        const MAX_SIZE = 5 * 1024 * 1024; // 5MB
        let isValid = true;
        
        const fileInputs = form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(function(input) {
            if (input.files.length > 0) {
                const file = input.files[0];
                if (file.size > MAX_SIZE) {
                    alert(`File ${file.name} exceeds 5MB limit`);
                    isValid = false;
                }
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    alert(`File ${file.name} must be a PDF`);
                    isValid = false;
                }
            }
        });
        return isValid;
    }

    // Form submission handler
    onboardingForm.addEventListener('submit', function(e) {
        // Validate files if present
        if (!validateFiles(this)) {
            e.preventDefault();
            return false;
        }

        // Basic form validation
        const requiredFields = this.querySelectorAll('[required]');
        let allValid = true;
        
        requiredFields.forEach(function(field) {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                allValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        if (!allValid) {
            e.preventDefault();
            alert('Please fill in all required fields.');
            return false;
        }

        // Show loading state on buttons
        const submitButtons = this.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(function(btn) {
            btn.disabled = true;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            // Restore button after 10 seconds as fallback
            setTimeout(function() {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }, 10000);
        });
    });

    // Remove validation styling on input
    const allInputs = onboardingForm.querySelectorAll('input, select, textarea');
    allInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });

    // Dynamic qualification management (for other qualifications step)
    let qualificationCount = 2; // Start with 2 shown qualifications
    const addQualificationBtn = document.getElementById('add_qualification_btn');
    
    if (addQualificationBtn) {
        addQualificationBtn.addEventListener('click', function() {
            qualificationCount++;
            const qualificationEntry = document.querySelector('.qualification-entry').cloneNode(true);
            
            // Update IDs and names
            qualificationEntry.querySelectorAll('input, select').forEach(function(field) {
                const baseName = field.name.replace(/_\d+$/, '').replace(/\d+$/, '');
                field.name = baseName + '_' + qualificationCount;
                field.id = field.id.replace(/_\d+$/, '').replace(/\d+$/, '') + '_' + qualificationCount;
                field.value = '';
                field.required = false; // Make additional qualifications optional
            });

            // Update labels
            qualificationEntry.querySelectorAll('label').forEach(function(label) {
                const forAttr = label.getAttribute('for');
                if (forAttr) {
                    label.setAttribute('for', forAttr.replace(/_\d+$/, '').replace(/\d+$/, '') + '_' + qualificationCount);
                }
            });

            // Add remove functionality
            const removeBtn = qualificationEntry.querySelector('.btn-outline-danger');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    qualificationEntry.remove();
                });
            }

            // Insert before the "Add New" button
            addQualificationBtn.parentElement.parentElement.insertBefore(qualificationEntry, addQualificationBtn.parentElement);
        });

        // Add remove functionality to existing qualification entries
        document.querySelectorAll('.qualification-entry .btn-outline-danger').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (document.querySelectorAll('.qualification-entry').length > 1) {
                    btn.closest('.qualification-entry').remove();
                } else {
                    alert('At least one qualification must remain.');
                }
            });
        });
    }

    // Auto-save functionality (optional)
    let autoSaveTimeout;
    function autoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(function() {
            const formData = new FormData(onboardingForm);
            formData.append('auto_save', '1');
            
            fetch('/onboarding/save', {
                method: 'POST',
                body: formData
            }).catch(function(error) {
                console.log('Auto-save failed:', error);
            });
        }, 5000); // Auto-save after 5 seconds of inactivity
    }

    // Attach auto-save to form changes
    allInputs.forEach(function(input) {
        input.addEventListener('input', autoSave);
    });
});
