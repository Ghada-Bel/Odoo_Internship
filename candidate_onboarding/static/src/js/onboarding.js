odoo.define('candidate_onboarding.onboarding', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.OnboardingNavigation = publicWidget.Widget.extend({
        selector: '#onboarding_main',
        events: {
            'click .btn-primary': '_onNext',
            'click .btn-secondary': '_onPrev',
        },

        _validateFiles: function(form) {
            const MAX_SIZE = 5 * 1024 * 1024; // 5MB
            let isValid = true;
            
            form.find('input[type="file"]').each(function() {
                if (this.files.length > 0) {
                    const file = this.files[0];
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
        },

        _onNext: function(ev) {
            ev.preventDefault();
            const form = this.$el.find('form');
            
            // Validate files first
            if (!this._validateFiles(form)) {
                return;
            }

            if (form[0].checkValidity()) {
                this._rpc({
                    route: '/onboarding/save',
                    params: {
                        next_step: true,
                        form_data: this._serializeForm(form),
                    },
                }).then(() => window.location.reload())
                  .fail(function(error) {
                    if (error.data.message) {
                        alert(error.data.message);
                    }
                });
            } else {
                form[0].reportValidity();
            }
        },

        _onPrev: function(ev) {
            ev.preventDefault();
            this._rpc({
                route: '/onboarding/save',
                params: {
                    prev_step: true,
                },
            }).then(() => window.location.reload());
        },

        _serializeForm: function(form) {
            const data = {};
            $(form).find('input, select, textarea').each(function() {
                if (this.type === 'file') {
                    if (this.files.length > 0) {
                        data[this.name] = this.files[0].name;
                    }
                } else {
                    data[this.name] = $(this).val();
                }
            });
            return data;
        },
    });
});
