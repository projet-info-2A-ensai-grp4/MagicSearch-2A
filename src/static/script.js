document.querySelector(".search-bar").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = e.target.querySelector("input");

  // URL complète de ton backend
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
    data.results.forEach(card => {
      const li = document.createElement("li");
      li.textContent = `${card.name} — ${card.type} (${card.distance.toFixed(3)})`;
      resultsList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = data.message || "Aucune carte trouvée.";
    resultsList.appendChild(li);
  }

  input.value = ""; 
});
