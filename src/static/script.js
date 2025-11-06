/* filepath: /home/victor/Work/MagicSearch-2A/src/static/script.js */

// Selected filters state
let selectedColors = [];
let lastSearchQuery = '';

// Search functionality
document.querySelector(".search-bar").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = e.target.querySelector("input");
  const limit = parseInt(document.getElementById('filterLimit').value) || 8;

  lastSearchQuery = input.value;

  const res = await fetch("https://user-tajas-551109-user-8000.user.lab.sspcloud.fr/search", {
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
    const res = await fetch("http://localhost:8000/search", {
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

    fetch("http://localhost:8000/search", {
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
