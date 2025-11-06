document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // empêche le rechargement de la page

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Hash du mot de passe en SHA-256 (comme côté FastAPI)
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const password_hash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Préparation de la requête POST
    const response = await fetch("https://user-tajas-551109-user-8000.user.lab.sspcloud.fr/login", {
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

    if (response.ok) {
        alert("Login successful! Welcome " + result.user.username);
        window.location.href = "../pages/index.html";
    } else {
        alert("Login failed: " + result.message);
    }
});
