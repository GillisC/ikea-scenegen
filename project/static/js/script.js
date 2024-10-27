
// Wait for the DOM to load before executing anything
document.addEventListener('DOMContentLoaded', function() {
    
    function handleButtonClick(groupSelector) {
        document.querySelector(groupSelector).addEventListener('click', (event) => {
            if (event.target.classList.contains('toggle-button')) {
                document.querySelectorAll(groupSelector + ' .toggle-button').forEach(button => button.classList.remove('active'));
                event.target.classList.add('active');
    
                const activeButton = document.querySelector(groupSelector + ' .active');
                console.log("Current selected button: " + activeButton.getAttribute('data-value'))
            }
        });
    }
    
    function handleMultiSelectButtonClick(groupSelector) {
        document.querySelector(groupSelector).addEventListener('click', (event) => {
            if (event.target.classList.contains('toggle-button')) {
                // Toggle the 'active' class instead of removing it for multi-select
                event.target.classList.toggle('active');
    
                // Collect all active buttons and log their values as a list
                const activeButtons = document.querySelectorAll(groupSelector + ' .toggle-button.active');
                const selectedValues = Array.from(activeButtons).map(button => button.getAttribute('data-value'));
    
                console.log("Current selected buttons: " + selectedValues.join(', '));
            }
        });
    }
    
    handleButtonClick("#style");
    handleButtonClick("#season");
    handleButtonClick("#time");
    handleButtonClick("#feeling");
    handleMultiSelectButtonClick("#materials");
    handleButtonClick("#audience");
    handleButtonClick("#pov");
    
    // This will run when the user presses the generate button
    document.getElementById('generate-button').addEventListener('click', function() {
        const testing = false;

        console.log("Generate button clicked");
        const styleValue = document.querySelector('#style .toggle-button.active')?.getAttribute('data-value');
        const seasonValue = document.querySelector('#season .toggle-button.active')?.getAttribute('data-value');
        const timeValue = document.querySelector('#time .toggle-button.active')?.getAttribute('data-value');
        const feelingValue = document.querySelector('#feeling .toggle-button.active')?.getAttribute('data-value');
        const materialsValues = Array.from(document.querySelectorAll('#materials .toggle-button.active')).map(button => button.getAttribute('data-value'));
        const audienceValue = document.querySelector('#audience .toggle-button.active')?.getAttribute('data-value');
        const povValue = document.querySelector('#pov .toggle-button.active')?.getAttribute('data-value');
        const selectedCountry = getSelectedCountry();

        const promptData = {
            style: styleValue,
            season: seasonValue,
            time: timeValue,
            feeling: feelingValue,
            materials: materialsValues,
            audience: audienceValue,
            pov: povValue,
            country: selectedCountry
        };
        console.log("Prompt data gathered: " + JSON.stringify(promptData, null, 2));

        // Change the status text to "Generating image..."
        const noImageText = document.getElementById('no-image-text');
        noImageText.textContent = "Generating image...";

        const loadingBarContainer = document.querySelector('.loading-bar-container');
        const loadingBar = document.getElementById('loading-bar');
        loadingBarContainer.style.display = 'block';

        
        loadingBar.style.width = '0%';
        loadingBar.style.animation = 'none';
        setTimeout(() => {
            loadingBar.style.animation = ''; 
        }, 10); 

        if (testing) {
            // Used for testing the frontend, database interactions without needing to send an api request
            console.log("Not sending a real api request, just testing");
            fetch('/test-generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(promptData), // Send promptData as JSON
            })
            .then(response => {
                console.log("Response from server:", response);
                return response.json()
            })
            .then(data => {
                console.log("Parsed JSON data:", data);
                if (data.image_url) {
                    loadingBarContainer.style.display = 'none';
                    console.log("Image URL received:", data.image_url);

                    const imageElement = document.getElementById('generated-image');
                    const noImageText = document.getElementById('no-image-text');
                    const imageLink = document.getElementById('download-link');

                    if (imageElement && data.image_url) {
                        imageElement.src = data.image_url; // Set the image source to the new image URL
                        imageLink.href = data.image_url; // Set the download url aswell

                        if (noImageText) {
                            noImageText.style.display = 'none';
                        }
                    }
                    
                } else if (data.error) {
                    console.error('Error:', data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        } else {
            fetch('/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(promptData), // Send promptData as JSON
            })
            .then(response => {
                console.log("Response from server:", response);
                return response.json()
            })
            .then(data => {
                console.log("Parsed JSON data:", data);
                if (data.image_url) {
                    loadingBarContainer.style.display = 'none';
                    console.log("Image URL received:", data.image_url);

                    const imageElement = document.getElementById('generated-image');
                    const noImageText = document.getElementById('no-image-text');
                    const imageLink = document.getElementById('download-link');

                    if (imageElement && data.image_url) {
                        imageElement.src = data.image_url; // Set the image source to the new image URL
                        imageLink.href = data.image_url; // Set the download url aswell

                        if (noImageText) {
                            noImageText.style.display = 'none';
                        }
                    }
                } else if (data.error) {
                    console.error('Error:', data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        
    });
});



