/* filepath: /home/victor/Work/MagicSearch-2A/src/static/script.js */

// Selected filters state
let selectedColors = [];
let lastSearchQuery = '';

// Authentication state management
function getUserSession() {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  if (!token) return null;

  try {
    // Decode JWT to get user info (simple base64 decode of payload)
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
  const accountLinks = document.querySelector('.account-links');

  if (user && accountLinks) {
    // User is logged in
    accountLinks.innerHTML = `
      <span class="username-display">Hello, ${user.username}</span>
      <button class="btn-outline logout-btn" id="logoutBtn">Log Out</button>
    `;

    document.getElementById('logoutBtn').addEventListener('click', () => {
      clearUserSession();
      window.location.href = 'index.html';
    });
  } else if (accountLinks) {
    // User is not logged in
    accountLinks.innerHTML = `
      <a href="login.html" class="btn-outline">Log In</a>
      <a href="register.html" class="btn-primary">Register</a>
    `;
  }
}

// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', () => {
  updateHeaderAuth();
});

// Search functionality
document.querySelector(".search-bar").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = e.target.querySelector("input");
  const limit = parseInt(document.getElementById('filterLimit').value) || 8;

  lastSearchQuery = input.value;

  const res = await fetch(`${API_CONFIG.BASE_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: lastSearchQuery, limit: limit }),
  });

  const data = await res.json();
  displayResults(data);
});

// Filter toggle
document.getElementById('filterToggle').addEventListener('click', function () {
  const panel = document.getElementById('filterPanel');
  this.classList.toggle('active');
  panel.classList.toggle('open');
});

// Color selection
document.querySelectorAll('.color-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const color = this.dataset.color;
    this.classList.toggle('active');

    if (selectedColors.includes(color)) {
      selectedColors = selectedColors.filter(c => c !== color);
    } else {
      selectedColors.push(color);
    }
  });
});

// Apply filters
document.getElementById('applyFilter').addEventListener('click', async function () {
  if (!lastSearchQuery.trim()) {
    alert('Please perform a search first!');
    return;
  }

  const filterBody = {
    text: lastSearchQuery,
    limit: parseInt(document.getElementById('filterLimit').value) || 8,
    filters: {}
  };

  // Add colors filter if any are selected
  if (selectedColors.length > 0) {
    filterBody.filters.colors = selectedColors;
  }

  // Add mana value filters
  const manaMin = document.getElementById('manaMin').value;
  const manaMax = document.getElementById('manaMax').value;

  if (manaMin) {
    filterBody.filters.mana_value__gte = parseInt(manaMin);
  }
  if (manaMax) {
    filterBody.filters.mana_value__lte = parseInt(manaMax);
  }

  console.log('Search with filters:', filterBody);

  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filterBody),
    });

    const data = await res.json();
    displayResults(data);
  } catch (error) {
    console.error('Filter error:', error);
  }
});

// Reset filters
document.getElementById('resetFilter').addEventListener('click', function () {
  // Reset colors
  selectedColors = [];
  document.querySelectorAll('.color-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  // Reset mana values
  document.getElementById('manaMin').value = '';
  document.getElementById('manaMax').value = '';

  // Reset limit
  document.getElementById('filterLimit').value = 8;

  // Re-run original search without filters
  if (lastSearchQuery) {
    const filterBody = {
      text: lastSearchQuery,
      limit: 8,
      filters: {}
    };

    fetch(`${API_CONFIG.BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filterBody),
    })
      .then(res => res.json())
      .then(data => displayResults(data));
  }
});

// Display results function
function displayResults(data) {
  const resultsList = document.getElementById("results");
  resultsList.innerHTML = "";

  if (data.results && data.results.length > 0) {
    resultsList.className = "results-grid";

    data.results.forEach(card => {
      const cardDiv = document.createElement("div");
      cardDiv.className = "card-item";

      const img = document.createElement("img");
      img.src = card.image_url;
      img.alt = card.name;
      img.className = "card-image";

      const info = document.createElement("p");
      info.textContent = card.distance !== undefined
        ? `Distance: ${card.distance.toFixed(3)}`
        : card.name;
      info.className = "card-info";

      // Add favorite button (only if user is logged in)
      const user = getUserSession();
      if (user) {
        const favoriteBtn = document.createElement('button');
        favoriteBtn.className = 'add-favorite-btn';
        favoriteBtn.innerHTML = '♥';
        favoriteBtn.title = 'Add to favorites';
        favoriteBtn.onclick = (e) => {
          e.stopPropagation();
          addToFavorites(card.id, favoriteBtn);
        };
        cardDiv.appendChild(favoriteBtn);
      }

      cardDiv.appendChild(img);
      cardDiv.appendChild(info);

      cardDiv.addEventListener('click', () => {
        openCardModal(card.image_url, card.name);
      });

      resultsList.appendChild(cardDiv);
    });

    setTimeout(() => {
      resultsList.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);

  } else {
    resultsList.className = "";
    const li = document.createElement("li");
    li.textContent = data.message || "No cards found.";
    resultsList.appendChild(li);
  }
}

// Modal functions
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

// Add to favorites function
async function addToFavorites(cardId, button) {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  if (!token) {
    alert('You need to be logged in to add favorites');
    return;
  }

  const cardIdInt = parseInt(cardId, 10);
  console.log('Adding favorite - cardId:', cardId, 'type:', typeof cardId, 'parsed:', cardIdInt);

  try {
    const payload = { card_id: cardIdInt };
    console.log('Request payload:', JSON.stringify(payload));

    const response = await fetch(`${API_CONFIG.BASE_URL}/favorite/add`, {
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
      
      // Handle specific error cases
      if (errorData.detail && errorData.detail.includes('already in favorites')) {
        alert('This card is already in your favorites!');
      } else {
        throw new Error(`Failed to add favorite: ${JSON.stringify(errorData)}`);
      }
      return;
    }

    // Success feedback
    button.classList.add('added');
    button.innerHTML = '✓';
    button.title = 'Added to favorites';
    
    // Disable button to prevent duplicate adds
    button.disabled = true;
    
    setTimeout(() => {
      button.innerHTML = '♥';
    }, 2000);

  } catch (error) {
    console.error('Error adding favorite:', error);
    alert('Failed to add favorite. Please try again.');
  }
}
