document.querySelector(".search-bar").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = e.target.querySelector("input");

  const res = await fetch("https://user-tajas-551109-user-8000.user.lab.sspcloud.fr/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: input.value }),
  });

  const data = await res.json();
  console.log(data);

  const resultsList = document.getElementById("results");
  resultsList.innerHTML = ""; 

  if (data.results && data.results.length > 0) {
    // Ajouter une classe pour la grille
    resultsList.className = "results-grid";

    data.results.forEach(card => {
      const cardDiv = document.createElement("div");
      cardDiv.className = "card-item";

      // Image de la carte
      const img = document.createElement("img");
      img.src = card.image_url;
      img.alt = card.name;
      img.className = "card-image";

      // Nom + type + distance
      const info = document.createElement("p");
      info.textContent = `${card.name} — ${card.type} (${card.distance.toFixed(3)})`;
      info.className = "card-info";

      cardDiv.appendChild(img);
      cardDiv.appendChild(info);
      resultsList.appendChild(cardDiv);
    });
  } else {
    resultsList.className = ""; // retirer classe grille si vide
    const li = document.createElement("li");
    li.textContent = data.message || "Aucune carte trouvée.";
    resultsList.appendChild(li);
  }

  input.value = ""; 
});
