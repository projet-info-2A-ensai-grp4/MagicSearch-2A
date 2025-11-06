document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // empêche le rechargement de la page

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const rememberMe = document.getElementById("rememberMe")?.checked || false;

    // Hash du mot de passe en SHA-256 (comme côté FastAPI)
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const password_hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Préparation de la requête POST
    const response = await fetch(`${API_CONFIG.BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password_hash: password_hash
        })
    });

    const result = await response.json();
    console.log(result);

    // Vérification que l'utilisateur existe avant d'accéder à .username
    if (result.user) {
        // Store token based on "Remember Me" checkbox
        if (rememberMe) {
            localStorage.setItem("access_token", result.access_token);
        } else {
            sessionStorage.setItem("access_token", result.access_token);
        }

        alert("Login successful! Welcome " + result.user.username);

        // Redirect to the page the user came from, or index.html by default
        const returnUrl = sessionStorage.getItem('login_return_url') || '../pages/index.html';
        sessionStorage.removeItem('login_return_url');
        window.location.href = returnUrl;
    } else {
        alert("Login failed: " + result.message);
    }
});
