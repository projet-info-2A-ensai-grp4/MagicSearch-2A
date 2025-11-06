// Check authentication status on page load
document.addEventListener('DOMContentLoaded', async function() {
    updateHeaderAuth();
    await checkAuthStatus();

    // Store return URL for login redirect
    setupLoginLinks();

    // Setup scroll indicator
    setupScrollIndicator();
});

// Setup scroll indicator to scroll to favorites section
function setupScrollIndicator() {
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            const favoritesSection = document.querySelector('.favorites-section');
            if (favoritesSection) {
                favoritesSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
}

// Setup login links to remember the current page
function setupLoginLinks() {
    document.querySelectorAll('a[href="login.html"]').forEach(link => {
        link.addEventListener('click', (e) => {
            // Store current page for redirect after login
            sessionStorage.setItem('login_return_url', 'favorites.html');
        });
    });
}

// Authentication state management (copied from script.js)
function getUserSession() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (!token) return null;

    try {
        // Decode JWT to get user info
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));

        // Check if token is expired
        if (decoded.exp && decoded.exp * 1000 < Date.now()) {
            clearUserSession();
            return null;
        }

        return decoded;
    } catch (e) {
        return null;
    }
}

function clearUserSession() {
    localStorage.removeItem('access_token');
    sessionStorage.removeItem('access_token');
    updateHeaderAuth();
}

function updateHeaderAuth() {
    const user = getUserSession();
    const accountLinks = document.getElementById('accountLinks');

    if (user && accountLinks) {
        accountLinks.innerHTML = `
            <span class="username-display">Hello, ${user.username}</span>
            <button class="btn-outline logout-btn" id="logoutBtn">Log Out</button>
        `;

        document.getElementById('logoutBtn').addEventListener('click', () => {
            clearUserSession();
            window.location.href = 'index.html';
        });
    } else if (accountLinks) {
        accountLinks.innerHTML = `
            <a href="login.html" class="btn-outline">Log In</a>
            <a href="register.html" class="btn-primary">Register</a>
        `;
    }
}

async function checkAuthStatus() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    if (!token) {
        showAuthRequired();
        return;
    }

    await loadFavorites(token);
}

function showAuthRequired() {
    document.getElementById('authRequired').style.display = 'flex';
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('favoritesList').innerHTML = '';

    // Hide the stats counter when not authenticated
    const statsSection = document.querySelector('.favorites-stats');
    if (statsSection) {
        statsSection.style.display = 'none';
    }
}

async function loadFavorites(token) {
    document.getElementById('authRequired').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'flex';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('favoritesList').innerHTML = '';

    // Show the stats section when loading favorites
    const statsSection = document.querySelector('.favorites-stats');
    if (statsSection) {
        statsSection.style.display = 'flex';
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/favorite`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load favorites');
        }

        const data = await response.json();
        const favorites = data.favorites || [];

        console.log('API Response:', data);
        console.log('Favorites:', favorites);

        document.getElementById('loadingSpinner').style.display = 'none';

        // Update the counter in the hero section
        document.getElementById('favoritesCount').textContent = favorites.length;

        if (favorites.length === 0) {
            document.getElementById('emptyState').style.display = 'flex';
        } else {
            displayFavorites(favorites);
        }

    } catch (error) {
        console.error('Error loading favorites:', error);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('favoritesList').innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ff6b6b;">
                <h3>Error loading favorites</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function displayFavorites(favorites) {
    const favoritesList = document.getElementById('favoritesList');
    favoritesList.innerHTML = '';

    favorites.forEach(card => {
        console.log('Displaying card:', card);

        const cardDiv = document.createElement('div');
        cardDiv.className = 'favorite-card';

        const img = document.createElement('img');
        img.src = card.image_url;
        img.alt = card.name;
        img.className = 'card-image';

        console.log('Image URL:', card.image_url);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-favorite-btn';
        removeBtn.textContent = '×';
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            removeFavorite(card.id);
        };

        cardDiv.appendChild(removeBtn);
        cardDiv.appendChild(img);

        cardDiv.onclick = () => openCardModal(card.image_url, card.name);

        favoritesList.appendChild(cardDiv);
    });
}

async function removeFavorite(cardId) {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (!token) {
        alert('You need to be logged in to remove favorites');
        return;
    }

    if (!confirm('Are you sure you want to remove this card from your favorites?')) {
        return;
    }

    const cardIdInt = parseInt(cardId, 10);
    console.log('Removing favorite - cardId:', cardId, 'type:', typeof cardId, 'parsed:', cardIdInt);

    try {
        const payload = { card_id: cardIdInt };
        console.log('Request payload:', JSON.stringify(payload));

        const response = await fetch(`${API_CONFIG.BASE_URL}/favorite/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Server error response:', errorData);
            throw new Error(`Failed to remove favorite: ${JSON.stringify(errorData)}`);
        }

        await loadFavorites(token);

    } catch (error) {
        console.error('Error removing favorite:', error);
        alert('Failed to remove favorite. Please try again.');
    }
}

function viewCardDetails(card) {
    console.log('Card details:', card);
}

function openCardModal(imageUrl, cardName) {
    const modal = document.createElement('div');
    modal.className = 'card-modal';

    const modalContent = document.createElement('div');
    modalContent.className = 'card-modal-content';

    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = cardName;
    img.className = 'card-modal-image';

    modalContent.appendChild(img);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    setTimeout(() => {
        modal.classList.add('active');
    }, 10);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeCardModal(modal);
        }
    });

    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeCardModal(modal);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
}

function closeCardModal(modal) {
    modal.classList.remove('active');
    setTimeout(() => {
        modal.remove();
    }, 300);
}

function logout() {
    localStorage.removeItem('access_token');
    sessionStorage.removeItem('access_token');
    window.location.href = 'index.html';
}
