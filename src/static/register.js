document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const termsChecked = document.getElementById('terms').checked;

        if (!termsChecked) {
            alert('You must agree to the terms and conditions.');
            return;
        }

        if (password.length < 8) {
            alert('Password must be at least 8 characters long.');
            return;
        }

        if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
            alert('Password must contain uppercase, lowercase letters, and numbers.');
            return;
        }

        const userData = {
            username: username,
            email: email,
            password: password
        };

        try {
            const response = await fetch('https://user-tajas-551109-user-8000.user.lab.sspcloud.fr/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Registration successful!');
                window.location.href = '../pages/index.html';
            } else {
                if (result.error === 'USERNAME ISSUE') {
                    alert('This username is invalid or already taken.');
                } else if (result.error === 'EMAIL ISSUE') {
                    alert('This email is already used.');
                } else {
                    alert('Error : ' + result.message);
                }
            }
        } catch (error) {
            alert('Connexion error.');
            console.error('Error:', error);
        }
    })
});
