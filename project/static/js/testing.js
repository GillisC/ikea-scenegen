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
handleButtonClick("#market");
handleButtonClick("#pov");


document.getElementById('generate-button').addEventListener('click', function() {
    
    console.log("You are currently in the testing environment, generate button clicked");
        
    const styleValue = document.querySelector('#style .toggle-button.active')?.getAttribute('data-value');
    const seasonValue = document.querySelector('#season .toggle-button.active')?.getAttribute('data-value');
    const timeValue = document.querySelector('#time .toggle-button.active')?.getAttribute('data-value');
    const feelingValue = document.querySelector('#feeling .toggle-button.active')?.getAttribute('data-value');
    const materialsValues = Array.from(document.querySelectorAll('#materials .toggle-button.active')).map(button => button.getAttribute('data-value'));
    const audienceValue = document.querySelector('#audience .toggle-button.active')?.getAttribute('data-value');
    const marketValue = document.querySelector('#market .toggle-button.active')?.getAttribute('data-value');
    const povValue = document.querySelector('#pov .toggle-button.active')?.getAttribute('data-value');
    
    console.log("Prompt data gathered");
    const promptData = {
        style: styleValue,
        season: seasonValue,
        time: timeValue,
        feeling: feelingValue,
        materials: materialsValues,
        audience: audienceValue,
        market: marketValue,
        pov: povValue 
    }

    console.log("The prompt data: " + promptData)

    
    // Debugging: Use a placeholder image URL
    const imageUrl = 'https://picsum.photos/1024'; // Will grab a random 1024x1024 image

    // Change the status text to "Generating image..."
    const statusText = document.getElementById('no-image-text');
    statusText.textContent = "Generating image...";

    // Show the loading bar when the "Generate" button is pressed
    const loadingBarContainer = document.querySelector('.loading-bar-container');
    const loadingBar = document.getElementById('loading-bar');
    loadingBarContainer.style.display = 'block'; // Make the loading bar visible

    // Reset the loading bar width to 0% and restart the animation
    loadingBar.style.width = '0%';
    loadingBar.style.animation = 'none'; // Reset the animation
    setTimeout(() => {
        loadingBar.style.animation = ''; // Trigger the animation again
    }, 10); // Small delay to reset the animation

    // Simulate the loading process (e.g., fake image generation)
    setTimeout(() => {
        // Hide the loading bar after a while
        loadingBarContainer.style.display = 'none';
        
        // Simulate receiving a generated image URL after a delay
        const imageElement = document.getElementById('generated-image');
        const downloadLink = document.getElementById('download-link');

        if (imageElement) {
            imageElement.src = imageUrl;  // Use the test image URL
            imageElement.style.display = 'block';  // Show the generated image
        }

        // Update the download link with the image URL
        if (downloadLink) {
            downloadLink.href = imageUrl;  // Set the download link to the test image URL
        }

        // Reset the status text
        statusText.style.display = 'none';
    }, 4000); // This delay should match the loading animation duration
});