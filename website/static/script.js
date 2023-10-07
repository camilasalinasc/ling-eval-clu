// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const defaultSearchOptions = document.querySelectorAll('.search-option');
    const searchResults = document.getElementById('search-results');

    // Functions to handle API key submission and model box selection
    const chatGPTBox = document.getElementById('chatgpt-box');
    const apiKeyInputBox = document.querySelector('.chatgpt-model-content');
    const apiKeyInput = document.getElementById('api-key-input');

    const llamaBox = document.getElementById('llama-box');
    const llamaModelSizeInputBox = document.querySelector('.llama-model-content');
    const llamaModelSizeInput = document.getElementById('llama-model-size');

    const vicunaBox = document.getElementById('vicuna-box');
    const vicunaModelSizeInputBox = document.querySelector('.vicuna-model-content');
    const vicunaModelSizeInput = document.getElementById('vicuna-model-size');

    const alpacaBox = document.getElementById('alpaca-box');
    const alpacaModelSizeInputBox = document.querySelector('.alpaca-model-content');
    const alpacaModelSizeInput = document.getElementById('alpaca-model-size');

    const flant5Box = document.getElementById('flant5-box');
    const flant5ModelSizeInputBox = document.querySelector('.flant5-model-content');
    const flant5ModelSizeInput = document.getElementById('flant5-model-size');

    // Get a reference to the user input container and title container
const userInputContainer = document.getElementById("user-input-container");
const titleContainer = document.getElementById("title-container");

// Function to set the top offset of the user input container
function setTopOffset() {
  const titleContainerHeight = titleContainer.offsetHeight;
  userInputContainer.style.top = titleContainerHeight + "px";
}

// Attach the scroll event listener
window.addEventListener("scroll", setTopOffset);

// Initial call to set the initial top offset
setTopOffset();


    // ------------------------------------ ChatGPT Model Box and API key submission ------------------------------------
    chatGPTBox.addEventListener('click', function () {
        // Toggle the visibility of the API key input box and button
        if (apiKeyInputBox.style.display === 'none') {
            apiKeyInputBox.style.display = 'block';
        } else {
            apiKeyInputBox.style.display = 'none';
        }
    });
    
    const submitApiKeyButton = document.getElementById('submit-api-key');
    submitApiKeyButton.addEventListener('click', function () {
        const apiKey = apiKeyInput.value.trim();
    
        if (apiKey !== '') {
            // Send the API key to the server for safe storage
            sendApiKeyToServer(apiKey);
        } else {
            alert('Please enter your API key.');
        }
    });
    
    // Prevent click events on the API key input box from propagating to the parent chatGPTBox
    apiKeyInput.addEventListener('click', function (event) {
        event.stopPropagation();
    });
    
    function sendApiKeyToServer(apiKey) {
        // For now, simply display an alert with the API key.
        alert(`API Key submitted: ${apiKey}`);
    }

    // ------------------------------------ LLaMA Model Box and Model Size selection ------------------------------------


    llamaBox.addEventListener('click', function () {
        // Toggle the visibility of the API key input box and button
        if (llamaModelSizeInputBox.style.display === 'none') {
            llamaModelSizeInputBox.style.display = 'block';
        } else {
            llamaModelSizeInputBox.style.display = 'none';
        }
    });

    llamaModelSizeInput.addEventListener('click', function (event) {
        event.stopPropagation();
    });

    // ------------------------------------ Vicuna Model Box and Model Size selection ------------------------------------

    vicunaBox.addEventListener('click', function () {
        // Toggle the visibility of the API key input box and button
        if (vicunaModelSizeInputBox.style.display === 'none') {
            vicunaModelSizeInputBox.style.display = 'block';
        } else {
            vicunaModelSizeInputBox.style.display = 'none';
        }
    });

    vicunaModelSizeInput.addEventListener('click', function (event) {
        event.stopPropagation();
    });

    // ------------------------------------ Alpaca Model Box and Model Size selection ------------------------------------

    alpacaBox.addEventListener('click', function () {
        // Toggle the visibility of the API key input box and button
        if (alpacaModelSizeInputBox.style.display === 'none') {
            alpacaModelSizeInputBox.style.display = 'block';
        } else {
            alpacaModelSizeInputBox.style.display = 'none';
        }
    });

    alpacaModelSizeInput.addEventListener('click', function (event) {
        event.stopPropagation();
    });

    // ------------------------------------ Flan-T5 Model Box and Model Size selection ------------------------------------

    flant5Box.addEventListener('click', function () {
        // Toggle the visibility of the API key input box and button
        if (flant5ModelSizeInputBox.style.display === 'none') {
            flant5ModelSizeInputBox.style.display = 'block';
        } else {
            flant5ModelSizeInputBox.style.display = 'none';
        }
    });

    flant5ModelSizeInput.addEventListener('click', function (event) {
        event.stopPropagation();
    });

document.querySelectorAll('.model-box').forEach(box => {
    box.addEventListener('click', function () {
        // Toggle the 'selected' class for the clicked box
        this.classList.toggle('selected');

        // Get the text of the clicked box
        const text = this.querySelector('h3').innerText;
        displayTextDifficulty(text);
    });
});

    // Function to perform a search and display results
    // Modify the performSearch function to fetch and display ground truth results
function performSearch(query) {
    // Perform the search logic here, e.g., querying a database
    // For demonstration purposes, have an object with ground truth data
    const groundTruth = {
        "cancer": {
            posTagging: "Noun",
            chunking: "NP",
            parsing: "S"
        },
        // Add other ground truth data here for different queries
    };

    const result = groundTruth[query];

    if (result) {
        // If ground truth data exists, display it
        const { posTagging, chunking, parsing } = result;
        searchResults.innerHTML = `
            <h3>Search results for: ${query}</h3>
            <h4>POS Tagging: </h4>
            <p>${posTagging}</p>
            <h4>Chunking: </h4>
            <p>${chunking}</p>
            <h4>Parsing: </h4>
            <p>${parsing}</p>
        `;
    } else {
        // If ground truth data is missing, display "No ground truth label"
        searchResults.innerHTML = `
            <h3>Search results for: ${query}</h3>
            <p>No ground truth label</p>
        `;
    }
}

    // Event listener for the search button
    searchButton.addEventListener('click', function () {
        const query = searchInput.value.trim();
        if (query !== '') {
            performSearch(query);
        }
    });

    // Event listener for default search options
    defaultSearchOptions.forEach(function (option) {
        option.addEventListener('click', function () {
            const query = option.getAttribute('data-query');
            searchInput.value = query;
            performSearch(query);
        });
    });
});

