odoo.define('candidate_portal.signup_validation', function (require) {
  'use strict';

  const publicWidget = require('web.public.widget');

  publicWidget.registry.SignupFormValidation = publicWidget.Widget.extend({
    selector: '#signupForm',
    start: function () {
      const nameRegex = /^[a-zA-Z' ]+$/;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      

      const firstName = document.getElementById('first_name');
      const lastName = document.getElementById('last_name');
      const email = document.getElementById('email');
      const phone = document.getElementById('phone');
      const password = document.getElementById('password');
      const confirmPassword = document.getElementById('confirm_password');

const iti = window.intlTelInput(phone, {
        initialCountry: 'tn', // Tunisia by default
        utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/utils.js',
      });

      firstName.addEventListener('input', () => {
        document.getElementById('firstNameError').classList.toggle('d-none', nameRegex.test(firstName.value));
      });

      lastName.addEventListener('input', () => {
        document.getElementById('lastNameError').classList.toggle('d-none', nameRegex.test(lastName.value));
      });

      email.addEventListener('input', () => {
        document.getElementById('emailError').classList.toggle('d-none', emailRegex.test(email.value));
      });

    
phone.addEventListener('input', () => {
        const valid = iti.isValidNumber();
        document.getElementById('phoneError').classList.toggle('d-none', valid);
      });


      confirmPassword.addEventListener('input', () => {
        const msg = document.getElementById('passwordMatchMessage');
        const match = password.value === confirmPassword.value;
        msg.classList.remove('d-none');
        msg.classList.toggle('text-success', match);
        msg.classList.toggle('text-danger', !match);
        msg.textContent = match ? "Passwords match" : "Passwords do not match";
      });
    },
  });
});

function togglePasswordVisibility(fieldId, iconId) {
  const input = document.getElementById(fieldId);
  const icon = document.getElementById(iconId);
  if (input && icon) {
    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";
    icon.classList.toggle("fa-eye");
    icon.classList.toggle("fa-eye-slash");
  }
}
