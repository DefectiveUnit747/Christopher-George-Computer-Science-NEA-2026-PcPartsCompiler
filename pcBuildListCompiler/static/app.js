function selectBrand(brand) {
    const buttons = document.querySelectorAll(".button-group button");
    buttons.forEach(btn => btn.classList.remove("selected"));

    const selectedBtn = document.getElementById(`btn-${brand}`);
    if (selectedBtn) selectedBtn.classList.add("selected");
}

function saveValues(budgetValue, aestheticsValue, futureValue) {
    const selectedBrand = document.querySelector(".button-group button.selected")?.dataset.brand;
    const valuesToSave = {
        budget: budgetValue,
        aesthetics: aestheticsValue,
        futurePref: futureValue,
        gpuPreference: selectedBrand
    };

    return fetch("/saveValues", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(valuesToSave)
    })

    .then(res => res.json())
}

document.addEventListener("DOMContentLoaded", () => {
    selectBrand("any"); //Makes the "any" button be selected as default
    const preview = document.getElementById("gamePreview");
    const mainContentPageButton = document.getElementById("mainContentPageButton");

    const budgetSlider = document.getElementById("budgetSlider"); //Actual slider
    const budgetValue = document.getElementById("budgetValue"); //Value of the slider
    const aestheticSlider = document.getElementById("aestheticSlider");
    const aestheticsValue = document.getElementById("aestheticsValue")
    const futureSlider = document.getElementById("futureSlider")
    const futureValue = document.getElementById("futureValue")

    const input = document.getElementById("gameSearchBar")
    const autoCompleteSuggestion = document.getElementById("searchSuggestion")
    const startButton = document.getElementById("startButton");

    budgetValue.textContent = budgetSlider.value;
    budgetSlider.addEventListener("input", () => {
        budgetValue.textContent = budgetSlider.value;
    }); //The value dynamically shows as the slider is used

    aestheticsValue.textContent  = aestheticSlider.value;
    aestheticSlider.addEventListener("input", () => {
        aestheticsValue.textContent = aestheticSlider.value;
    });

    futureValue.textContent = futureSlider.value;
    futureSlider.addEventListener("input", () => {
        futureValue.textContent = futureSlider.value;
    });

    document.querySelectorAll(".button-group button").forEach(btn => {
        btn.addEventListener("click", () => {
            selectBrand(btn.dataset.brand)
        })
    })

    input.addEventListener("input", () => { //Triggers when typing in the search bar
        const query = input.value.trim(); //removes whitespaces
        if (query.length < 3) {
           autoCompleteSuggestion.innerHTML = "";
           return;
        }

        fetch(`/searchForGame?q=${encodeURIComponent(query)}`) //Sends get request to the backend flask route
            .then(res => res.json())
            .then(games => {

                autoCompleteSuggestion.innerHTML = games.map(game => //map() turns the array containing objects of the game suggestions into strings of names in a new array
                    `<div class="suggestion-item">${game.name}</div>`
                ).join("");

                document.querySelectorAll(".suggestion-item").forEach((item, index)  => { //Finds all items with the class suggestion-item
                    item.addEventListener("click", () => {
                        input.value = games[index].name
                        autoCompleteSuggestion.innerHTML = "";

                        preview.innerHTML = `
                            <div class="preview-box">
                                ${games[index].background_image ? `<img src="${games[index].background_image}" class="preview-image">` : ""}
                                <p><strong>Selected:</strong> ${games[index].name}</p>
                            </div>
                        `;
                    })
                })
            })
            .catch(error => { //Clears suggestions where there are any errors e.g. network or connecting to API
                console.error('Error fetching games:', error);
                autoCompleteSuggestion.innerHTML = "";
            });
    })

    startButton.addEventListener("click", () => {
        window.location.href = "/homePage/mainContent";
    })

    mainContentPageButton.addEventListener("click", () => { //Called a callback function - so when I "click" calls function
        const selectedGame = input.value;
        if (! selectedGame) { //if blank
            alert ("PLease select a Game!")
            return;
        }

        const budget = budgetSlider.value;
        const aesthetics = aestheticSlider.value;
        const future = futureSlider.value;

        saveValues(budget, aesthetics, future)
        .then(data => console.log("Preferences saved:", data))
        .catch(err => console.error("Error saving preferences:", err));

        //Fetch - built-in browser api to make HTTP requests
        fetch("/saveGame", {
            method: "POST",
            headers: {"Content-Type": "application/json"}, //Notifies that request body is JSON
            body: JSON.stringify({name: selectedGame}) //Turns object --> json
        })
        .then(res => res.json())//After request finishes, converts response to JS object
        .catch(err => console.error("Error Saving game:", err)); //Runs if the request fails

        window.location.href = "/homePage/mainContent/Results";
    })
});