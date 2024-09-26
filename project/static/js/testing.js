document.getElementById('generate-button').addEventListener('click', function() {
    // Debugging: Use a placeholder image URL
    const imageUrl = 'https://picsum.photos/1024'; // Test image URL

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