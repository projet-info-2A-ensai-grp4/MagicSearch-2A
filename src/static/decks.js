// Check authentication status on page load
document.addEventListener('DOMContentLoaded', async function() {
    updateHeaderAuth();
    await checkAuthStatus();

    // Store return URL for login redirect
    setupLoginLinks();

    // Setup scroll indicator
    setupScrollIndicator();

    // Setup modal event listeners
    setupModals();
});

// Setup scroll indicator to scroll to decks section
function setupScrollIndicator() {
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            const decksSection = document.querySelector('.decks-section');
            if (decksSection) {
                decksSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
}

// Setup login links to remember the current page
function setupLoginLinks() {
    document.querySelectorAll('a[href="login.html"]').forEach(link => {
        link.addEventListener('click', (e) => {
            // Store current page for redirect after login
            sessionStorage.setItem('login_return_url', 'decks.html');
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
    const user = getUserSession();
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    if (!token || !user) {
        showAuthRequired();
        return;
    }

    await loadUserDecks(token, user.user_id);
}

function showAuthRequired() {
    document.getElementById('authRequired').style.display = 'flex';
    document.getElementById('loadingSpinner').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('decksList').innerHTML = '';

    // Hide the stats section when not authenticated
    const statsSection = document.querySelector('.decks-stats');
    if (statsSection) {
        statsSection.style.display = 'none';
    }

    // Hide create deck button when not authenticated
    const createDeckBtn = document.getElementById('createDeckBtn');
    if (createDeckBtn) {
        createDeckBtn.style.display = 'none';
    }
}

async function loadUserDecks(token, userId) {
    document.getElementById('authRequired').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'flex';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('decksList').innerHTML = '';

    // Show the stats section when loading decks
    const statsSection = document.querySelector('.decks-stats');
    if (statsSection) {
        statsSection.style.display = 'flex';
    }

    // Show create deck button when authenticated
    const createDeckBtn = document.getElementById('createDeckBtn');
    if (createDeckBtn) {
        createDeckBtn.style.display = 'block';
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/deck/user/read?user_id=${userId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load decks');
        }

        const data = await response.json();
        const decks = data.results || [];

        console.log('API Response:', data);
        console.log('Decks:', decks);

        document.getElementById('loadingSpinner').style.display = 'none';

        // Update the counters in the hero section
        document.getElementById('decksCount').textContent = decks.length;

        if (decks.length === 0) {
            document.getElementById('emptyState').style.display = 'flex';
        } else {
            displayDecks(decks);
        }

    } catch (error) {
        console.error('Error loading decks:', error);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('decksList').innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ff6b6b;">
                <h3>Error loading decks</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function displayDecks(decks) {
    const decksList = document.getElementById('decksList');
    decksList.innerHTML = '';

    decks.forEach(deck => {
        console.log('Displaying deck:', deck);

        const deckDiv = document.createElement('div');
        deckDiv.className = 'deck-card';

        deckDiv.innerHTML = `
            <div class="deck-header">
                <h3 class="deck-name">${deck.name || 'Unnamed Deck'}</h3>
            </div>
            <div class="deck-actions">
                <button class="btn-outline view-edit-btn" onclick="viewDeck(${deck.id})">View & Edit</button>
                <button class="btn-danger delete-deck-btn">Delete</button>
            </div>
        `;

        decksList.appendChild(deckDiv);
    });
}

// Modal setup and event listeners
function setupModals() {
    // Create Deck Modal
    const createDeckBtn = document.getElementById('createDeckBtn');
    const createFirstDeckBtn = document.getElementById('createFirstDeckBtn');
    const createDeckModal = document.getElementById('createDeckModal');
    const closeCreateModal = document.getElementById('closeCreateModal');
    const cancelCreateBtn = document.getElementById('cancelCreateBtn');
    const createDeckForm = document.getElementById('createDeckForm');

    if (createDeckBtn) {
        createDeckBtn.addEventListener('click', () => {
            createDeckModal.classList.add('active');
        });
    }

    if (createFirstDeckBtn) {
        createFirstDeckBtn.addEventListener('click', () => {
            createDeckModal.classList.add('active');
        });
    }

    if (closeCreateModal) {
        closeCreateModal.addEventListener('click', () => {
            createDeckModal.classList.remove('active');
        });
    }

    if (cancelCreateBtn) {
        cancelCreateBtn.addEventListener('click', () => {
            createDeckModal.classList.remove('active');
        });
    }

    if (createDeckForm) {
        createDeckForm.addEventListener('submit', handleCreateDeck);
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === createDeckModal) {
            createDeckModal.classList.remove('active');
        }
    });
}

// Deck creation
async function handleCreateDeck(e) {
    e.preventDefault();

    const user = getUserSession();
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    if (!user || !token) {
        alert('You need to be logged in to create a deck');
        return;
    }

    const formData = new FormData(e.target);
    const deckName = formData.get('deckName');

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/deck/player/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: user.user_id,
                name: deckName,
                type: 'Casual'  // Default type since we removed the format field
            })
        });

        if (!response.ok) {
            throw new Error('Failed to create deck');
        }

        // Close modal and refresh decks
        document.getElementById('createDeckModal').classList.remove('active');
        document.getElementById('createDeckForm').reset();

        // Reload decks
        await loadUserDecks(token, user.user_id);
    } catch (error) {
        console.error('Error creating deck:', error);
        alert('Failed to create deck. Please try again.');
    }
}

// View deck functionality
async function viewDeck(deckId) {
    const user = getUserSession();
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    if (!user || !token) {
        alert('You need to be logged in to view a deck');
        return;
    }

    try {
        // Get deck details
        const deckResponse = await fetch(`${API_CONFIG.BASE_URL}/deck/user/read?user_id=${user.user_id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!deckResponse.ok) {
            throw new Error('Failed to load deck details');
        }

        const deckData = await deckResponse.json();
        const deck = deckData.results.find(d => d.id === deckId);

        if (!deck) {
            throw new Error('Deck not found');
        }

        // Get cards in deck
        const cardsResponse = await fetch(`${API_CONFIG.BASE_URL}/deck/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                deck_id: deckId
            })
        });

        let cards = [];
        if (cardsResponse.ok) {
            const cardsData = await cardsResponse.json();
            cards = cardsData.results || [];
            console.log('Cards data:', cardsData);
            console.log('Cards:', cards);
        } else {
            // Deck might be empty, which could cause a 404 or other error
            console.log('Failed to load cards (deck might be empty):', cardsResponse.status, cardsResponse.statusText);
        }

        // Store deck info for later use
        sessionStorage.setItem('current_deck_id', deckId);
        sessionStorage.setItem('current_deck_name', deck.name);

        // Show deck view modal
        showDeckViewModal(deck, cards);

    } catch (error) {
        console.error('Error viewing deck:', error);
        alert('Failed to load deck. Please try again.');
    }
}

function showDeckViewModal(deck, cards) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('deckViewModal');
    if (!modal) {
        modal = createDeckViewModal();
        document.body.appendChild(modal);
    }

    // Update modal content
    document.getElementById('deckViewTitle').textContent = deck.name;

    const deckViewContent = document.getElementById('deckViewContent');

    if (cards.length === 0) {
        // Deck is empty
        deckViewContent.innerHTML = `
            <div class="empty-deck">
                <h3>This deck is empty</h3>
                <p>Add some cards to get started!</p>
                <button class="btn-primary" onclick="goToSearch()">Search for Cards</button>
            </div>
        `;
    } else {
        // Deck has cards
        deckViewContent.innerHTML = `
            <div class="deck-actions">
                <button class="btn-primary" onclick="goToSearch()">Add More Cards</button>
            </div>
            <div class="cards-grid">
                ${cards.map(card => `
                    <div class="card-item">
                        <img src="${card.image_url || ''}" alt="${card.name}" class="card-image">
                        <div class="card-info">
                            <h4>${card.name}</h4>
                            <p>Quantity: ${card.quantity || 1}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    modal.classList.add('active');
}

function createDeckViewModal() {
    const modal = document.createElement('div');
    modal.id = 'deckViewModal';
    modal.className = 'modal';

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="deckViewTitle">Deck View</h2>
                <span class="close-btn" onclick="closeDeckViewModal()">&times;</span>
            </div>
            <div id="deckViewContent" class="deck-view-content">
                <!-- Content will be dynamically generated -->
            </div>
        </div>
    `;

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeDeckViewModal();
        }
    });

    return modal;
}

function closeDeckViewModal() {
    const modal = document.getElementById('deckViewModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function goToSearch() {
    // Store return information
    sessionStorage.setItem('return_to_deck_view', 'true');
    // Redirect to home page
    window.location.href = 'index.html';
}
