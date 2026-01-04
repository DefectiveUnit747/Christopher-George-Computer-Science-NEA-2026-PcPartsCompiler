function selectBrand(brand) {
    const buttons = document.querySelectorAll(".button-group button");
    buttons.forEach(btn => btn.classList.remove("selected"));

    const selectedBtn = document.getElementById(`btn-${brand}`);
    if (selectedBtn) selectedBtn.classList.add("selected");
}

function saveValues(budgetValue, efficiencyValue, futureValue) {
    const selectedBrand = document.querySelector(".button-group button.selected")?.dataset.brand;

    const valuesToSave = {
        budget: budgetValue,
        aesthetics: efficiencyValue,
        futurePref: futureValue,
        gpuPreference: selectedBrand
    };

    return fetch("/saveValues", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(valuesToSave)
    }).then(res => res.json());
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM loaded, pathname:", window.location.pathname);

    // Check if we're on the main content page or results page
    const isResultsPage = window.location.pathname.includes("/results");
    const isMainContentPage = document.getElementById("mainContentPageButton") !== null;

    console.log("Is results page:", isResultsPage);
    console.log("Is main content page:", isMainContentPage);

    // Main content page functionality
    if (isMainContentPage) {
        selectBrand("any");

        const preview = document.getElementById("gamePreview");
        const mainContentPageButton = document.getElementById("mainContentPageButton");

        const budgetSlider = document.getElementById("budgetSlider");
        const budgetValue = document.getElementById("budgetValue");

        const efficiencySlider = document.getElementById("efficiencySlider");
        const efficiencyValue = document.getElementById("efficiencyValue");

        const futureSlider = document.getElementById("futureSlider");
        const futureValue = document.getElementById("futureValue");

        const input = document.getElementById("gameSearchBar");
        const autoCompleteSuggestion = document.getElementById("searchSuggestion");

        // Slider live updates
        budgetValue.textContent = budgetSlider.value;
        budgetSlider.addEventListener("input", () => {
            budgetValue.textContent = budgetSlider.value;
        });

        efficiencyValue.textContent = efficiencySlider.value;
        efficiencySlider.addEventListener("input", () => {
            efficiencyValue.textContent = efficiencySlider.value;
        });

        futureValue.textContent = futureSlider.value;
        futureSlider.addEventListener("input", () => {
            futureValue.textContent = futureSlider.value;
        });

        // Brand selection buttons
        document.querySelectorAll(".button-group button").forEach(btn => {
            btn.addEventListener("click", () => {
                selectBrand(btn.dataset.brand);
            });
        });

        // Game search
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                const query = input.value.trim();
                if (query.length < 3) {
                    autoCompleteSuggestion.innerHTML = "";
                    return;
                }

                fetch(`/searchForGame?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(games => {
                        autoCompleteSuggestion.innerHTML = games.map(game =>
                            `<div class="suggestion-item">${game.name}</div>`
                        ).join("");

                        document.querySelectorAll(".suggestion-item").forEach((item, index) => {
                            item.addEventListener("click", () => {
                                input.value = games[index].name;
                                autoCompleteSuggestion.innerHTML = "";

                                preview.innerHTML = `
                                    <div class="preview-box">
                                        ${games[index].background_image ? `<img src="${games[index].background_image}" class="preview-image">` : ""}
                                        <p><strong>Selected:</strong> ${games[index].name}</p>
                                    </div>
                                `;
                            });
                        });
                    })
                    .catch(() => autoCompleteSuggestion.innerHTML = "");
            }
        });

        // Continue button
        if (mainContentPageButton) {
            mainContentPageButton.addEventListener("click", () => {
                const selectedGame = input.value;
                if (!selectedGame) {
                    alert("Please select a game!");
                    return;
                }

                const budget = budgetSlider.value;
                const aesthetics = efficiencySlider.value;
                const future = futureSlider.value;

                saveValues(budget, aesthetics, future)
                    .then(() => {
                        return fetch("/saveGame", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ name: selectedGame })
                        });
                    })
                    .then(() => {
                        window.location.href = "/homePage/mainContent/results";
                    })
                    .catch(err => console.error("Error saving data:", err));
            });
        }
    }

    // Results page functionality
    if (isResultsPage) {
        console.log("Results page detected, loading build...");
        loadBuildResults();

        const backButton = document.getElementById("backButton");
        const exportButton = document.getElementById("exportButton");

        if (backButton) {
            backButton.addEventListener("click", () => {
                window.location.href = "/homePage/mainContent";
            });
        }

        if (exportButton) {
            exportButton.addEventListener("click", exportBuild);
        }
    }
});

// Results page functions
async function loadBuildResults() {
    console.log("loadBuildResults() called");
    const buildResults = document.getElementById("buildResults");

    if (!buildResults) {
        console.error("buildResults element not found!");
        return;
    }

    // Show loading state
    buildResults.innerHTML = '<div class="loading">Generating your perfect build...</div>';

    try {
        console.log("Fetching /generateBuild...");
        // Call your algorithm endpoint
        const response = await fetch("/generateBuild", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        console.log("Response status:", response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error response:", errorData);
            throw new Error(errorData.error || "Failed to generate build");
        }

        const buildData = await response.json();
        console.log("Build data received:", buildData);
        displayBuild(buildData);

    } catch (error) {
        console.error("Error loading build:", error);
        buildResults.innerHTML = `<div class="error">Failed to generate build: ${error.message}</div>`;
    }
}

function displayBuild(buildData) {
    console.log("displayBuild() called with:", buildData);
    const buildResults = document.getElementById("buildResults");
    const priceValue = document.getElementById("priceValue");

    if (!buildResults || !priceValue) {
        console.error("Required elements not found!");
        return;
    }

    buildResults.innerHTML = "";
    let totalPrice = 0;

    const componentOrder = ["cpu", "motherboard", "ram", "gpu", "psu", "case", "storage"];
    const componentNames = {
        "cpu": "Processor",
        "motherboard": "Motherboard",
        "ram": "Memory",
        "gpu": "Graphics Card",
        "psu": "Power Supply",
        "case": "Case",
        "storage": "Storage"
    };

    componentOrder.forEach(component => {
        if (buildData[component]) {
            const part = buildData[component];
            totalPrice += part.price;

            const partCard = document.createElement("div");
            partCard.className = "partCard";

            // Convert Windows backslashes to forward slashes for web
            const imagePath = part.imagePath.replace(/\\/g, '/');

            partCard.innerHTML = `
                <img src="/static/${imagePath}" alt="${part.name}" class="partImage" onerror="this.src='/static/productImages/placeholder.jpg'">
                <div class="partInfo">
                    <div class="partType">${componentNames[component]}</div>
                    <div class="partName">${part.name}</div>
                    <div class="partPrice">£${part.price.toFixed(2)}</div>
                    <a href="${part.url}" target="_blank" class="partLink">View Product →</a>
                </div>
            `;

            buildResults.appendChild(partCard);
        }
    });

    priceValue.textContent = totalPrice.toFixed(2);
    console.log("Total price:", totalPrice);
}

function exportBuild() {
    const buildResults = document.getElementById("buildResults");
    const priceValue = document.getElementById("priceValue");

    if (!buildResults || !priceValue) return;

    const totalPrice = priceValue.textContent;

    // Create text content for export
    let exportText = "=== YOUR CUSTOM PC BUILD ===\n\n";

    const partCards = buildResults.querySelectorAll(".partCard");
    partCards.forEach(card => {
        const type = card.querySelector(".partType").textContent;
        const name = card.querySelector(".partName").textContent;
        const price = card.querySelector(".partPrice").textContent;
        const url = card.querySelector(".partLink").href;

        exportText += `${type}\n`;
        exportText += `${name}\n`;
        exportText += `${price}\n`;
        exportText += `${url}\n\n`;
    });

    exportText += `TOTAL PRICE: £${totalPrice}\n`;

    // Create and download file
    const blob = new Blob([exportText], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pc_build.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}