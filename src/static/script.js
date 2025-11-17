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
  setupHistoryFeature();

  // Check if returning from deck view
  const returnToDeckView = sessionStorage.getItem('return_to_deck_view');
  if (returnToDeckView === 'true') {
    sessionStorage.removeItem('return_to_deck_view');

    // Show message to user
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
      const returnMessage = document.createElement('div');
      returnMessage.className = 'return-message';
      returnMessage.innerHTML = `
        <p><strong>🔍 Search for cards to add to your deck</strong></p>
        <p>Use the "+D" button on cards to add them to your deck</p>
      `;
      searchContainer.insertBefore(returnMessage, searchContainer.firstChild);

      // Auto-remove message after 10 seconds
      setTimeout(() => {
        if (returnMessage.parentNode) {
          returnMessage.remove();
        }
      }, 10000);
    }
  }
});

// History feature setup
function setupHistoryFeature() {
  const searchInput = document.getElementById('searchInput');
  const historyContainer = document.getElementById('historyContainer');
  const historyClose = document.getElementById('historyClose');

  if (!searchInput || !historyContainer) return;

  // Show history when user focuses on search input
  searchInput.addEventListener('focus', async () => {
    const user = getUserSession();
    if (user) {
      await loadAndDisplayHistory();
    }
  });

  // Close history when clicking the close button
  if (historyClose) {
    historyClose.addEventListener('click', () => {
      historyContainer.style.display = 'none';
    });
  }

  // Close history when clicking outside
  document.addEventListener('click', (e) => {
    if (!historyContainer.contains(e.target) && !searchInput.contains(e.target)) {
      historyContainer.style.display = 'none';
    }
  });
}

// Load and display user history
async function loadAndDisplayHistory() {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  if (!token) return;

  try {
    const res = await fetch(`${API_CONFIG.BASE_URL}/history`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!res.ok) {
      console.error('Failed to load history');
      return;
    }

    const data = await res.json();
    displayHistory(data.history);
  } catch (error) {
    console.error('Error loading history:', error);
  }
}

// Display history in the UI
function displayHistory(historyItems) {
  const historyContainer = document.getElementById('historyContainer');
  const historyList = document.getElementById('historyList');

  if (!historyList) return;

  historyList.innerHTML = '';

  if (!historyItems || historyItems.length === 0) {
    historyList.innerHTML = '<div class="history-empty">No search history yet</div>';
  } else {
    // Sort by date (most recent first) and display
    historyItems.reverse().forEach(item => {
      const historyItem = document.createElement('div');
      historyItem.className = 'history-item';

      const itemText = document.createElement('span');
      itemText.className = 'history-item-text';
      itemText.textContent = item.prompt || item;

      const itemDate = document.createElement('span');
      itemDate.className = 'history-item-date';
      if (item.date) {
        const date = new Date(item.date);
        itemDate.textContent = date.toLocaleDateString();
      }

      historyItem.appendChild(itemText);
      if (item.date) {
        historyItem.appendChild(itemDate);
      }

      // Click to use this search query
      historyItem.addEventListener('click', () => {
        const searchInput = document.getElementById('searchInput');
        searchInput.value = item.prompt || item;
        historyContainer.style.display = 'none';
        // Optionally trigger search automatically
        // searchInput.closest('form').dispatchEvent(new Event('submit'));
      });

      historyList.appendChild(historyItem);
    });
  }

  historyContainer.style.display = 'block';
}

// Search functionality
document.querySelector(".search-bar").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById('searchInput');
  const limit = parseInt(document.getElementById('filterLimit').value) || 8;

  lastSearchQuery = input.value;

  // Add to history if user is logged in
  const user = getUserSession();
  if (user) {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    try {
      await fetch(`${API_CONFIG.BASE_URL}/history/add`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: lastSearchQuery })
      });
    } catch (error) {
      console.error('Failed to add to history:', error);
    }
  }

  const res = await fetch(`${API_CONFIG.BASE_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: lastSearchQuery, limit: limit }),
  });

  const data = await res.json();
  displayResults(data);

  // Hide history after search
  const historyContainer = document.getElementById('historyContainer');
  if (historyContainer) {
    historyContainer.style.display = 'none';
  }
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
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'card-buttons';

        const favoriteBtn = document.createElement('button');
        favoriteBtn.className = 'add-favorite-btn';
        favoriteBtn.innerHTML = '♥';
        favoriteBtn.title = 'Add to favorites';
        favoriteBtn.onclick = (e) => {
          e.stopPropagation();
          addToFavorites(card.id, favoriteBtn);
        };

        const deckBtn = document.createElement('button');
        deckBtn.className = 'add-deck-btn';
        deckBtn.innerHTML = '+D';
        deckBtn.title = 'Add to deck';
        deckBtn.onclick = (e) => {
          e.stopPropagation();
          showAddToDeckModal(card);
        };

        buttonsContainer.appendChild(favoriteBtn);
        buttonsContainer.appendChild(deckBtn);
        cardDiv.appendChild(buttonsContainer);
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

// Add to deck functionality
async function showAddToDeckModal(card) {
  const user = getUserSession();
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

  if (!user || !token) {
    alert('You need to be logged in to add cards to a deck');
    return;
  }

  try {
    // Fetch user's decks
    const response = await fetch(`${API_CONFIG.BASE_URL}/deck/user/read`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to load decks');
    }

    const data = await response.json();
    let decks = data.results || [];

    console.log('Full API response:', data);
    console.log('Raw decks data:', decks);

    if (decks.length === 0) {
      alert('You need to create a deck first! Go to the Decks page to create one.');
      return;
    }

    // Transform deck data to ensure we have id and name
    decks = decks.map((deck, index) => {
      if (typeof deck === 'number') {
        // It's just an ID
        return {
          id: deck,
          name: `Deck ${deck}`
        };
      } else if (deck && typeof deck === 'object') {
        // It's an object, find the right properties
        return {
          id: deck.deck_id || deck.id || deck.deckId || index,
          name: deck.name || deck.deck_name || deck.deckName || `Deck ${deck.deck_id || deck.id || index}`
        };
      } else {
        // Fallback
        return {
          id: index,
          name: `Deck ${index}`
        };
      }
    });

    console.log('Transformed decks:', decks);

    // Show deck selection modal
    showDeckSelectionModal(card, decks);

  } catch (error) {
    console.error('Error loading decks:', error);
    alert('Failed to load decks. Please try again.');
  }
}

function showDeckSelectionModal(card, decks) {
  // Create modal if it doesn't exist
  let modal = document.getElementById('deckSelectionModal');
  if (!modal) {
    modal = createDeckSelectionModal();
    document.body.appendChild(modal);
  }

  // Update modal content
  const deckSelect = document.getElementById('deckSelect');
  console.log('Available decks:', decks);
  deckSelect.innerHTML = decks.map(deck => {
    const deckId = deck.id || deck.deck_id;
    const deckName = deck.name || `Deck ${deckId}`;
    console.log('Deck:', deck, 'ID:', deckId, 'Name:', deckName);
    return `<option value="${deckId}">${deckName}</option>`;
  }).join('');

  document.getElementById('selectedCardName').textContent = card.name;

  // Set up form submission
  const form = document.getElementById('addToDeckForm');
  form.onsubmit = async (e) => {
    e.preventDefault();
    const deckId = deckSelect.value;
    console.log('Selected deckId:', deckId, 'type:', typeof deckId);
    console.log('Select element:', deckSelect);
    console.log('Select innerHTML:', deckSelect.innerHTML);
    console.log('Select options:', Array.from(deckSelect.options).map(opt => ({value: opt.value, text: opt.text})));
    console.log('Card:', card, 'Card ID:', card.id);

    if (!deckId || deckId === '' || deckId === 'null') {
      alert('Please select a deck');
      console.error('No deck selected. Available options:', Array.from(deckSelect.options));
      return;
    }

    await addCardToDeck(card.id, deckId);
    closeDeckSelectionModal();
  };

  modal.classList.add('active');
}

function createDeckSelectionModal() {
  const modal = document.createElement('div');
  modal.id = 'deckSelectionModal';
  modal.className = 'modal';

  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h2>Add Card to Deck</h2>
        <span class="close-btn" onclick="closeDeckSelectionModal()">&times;</span>
      </div>
      <form id="addToDeckForm">
        <div class="form-group">
          <label>Card:</label>
          <p id="selectedCardName" style="color: #ff6b35; font-weight: bold;"></p>
        </div>
        <div class="form-group">
          <label for="deckSelect">Select Deck:</label>
          <select id="deckSelect" required>
            <!-- Options will be populated dynamically -->
          </select>
        </div>
        <div class="form-actions">
          <button type="button" onclick="closeDeckSelectionModal()" class="btn-outline">Cancel</button>
          <button type="submit" class="btn-primary">Add to Deck</button>
        </div>
      </form>
    </div>
  `;

  // Close modal when clicking outside
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeDeckSelectionModal();
    }
  });

  return modal;
}

function closeDeckSelectionModal() {
  const modal = document.getElementById('deckSelectionModal');
  if (modal) {
    modal.classList.remove('active');
  }
}

async function addCardToDeck(cardId, deckId) {
  const user = getUserSession();
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

  if (!user || !token) {
    alert('You need to be logged in to add cards to a deck');
    return;
  }

  console.log('addCardToDeck called with:', { cardId, deckId });

  // Validate inputs
  if (!cardId || !deckId || deckId === '' || deckId === 'null' || deckId === 'undefined') {
    alert('Missing card ID or deck ID');
    console.error('Missing or invalid IDs:', { cardId, deckId, typeOfDeckId: typeof deckId });
    return;
  }

  const deckIdInt = parseInt(deckId);
  const cardIdInt = parseInt(cardId);

  if (isNaN(deckIdInt) || isNaN(cardIdInt)) {
    alert('Invalid ID format');
    console.error('NaN values:', { deckId, deckIdInt, cardId, cardIdInt });
    return;
  }

  const payload = {
    deck_id: deckIdInt,
    card_id: cardIdInt
  };

  console.log('Payload to send:', payload);

  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/deck/card/add`, {
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

      if (errorData.detail && errorData.detail.includes('already exists')) {
        alert('This card is already in the selected deck!');
      } else {
        throw new Error(`Failed to add card to deck: ${JSON.stringify(errorData)}`);
      }
      return;
    }

    alert('Card successfully added to deck!');

  } catch (error) {
    console.error('Error adding card to deck:', error);
    alert('Failed to add card to deck. Please try again.');
  }
}
