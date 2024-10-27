function toggleStar(button, imageId) {
    // Check the current state (filled or unfilled)
    if (button.innerHTML === '★') {
        // Star is filled, toggle to unfilled
        button.innerHTML = '☆'; // Change to unfilled star
        button.classList.remove('filled');
        button.classList.add('unfilled');
        
        // Optionally, remove the saved image
    } else {
        // Star is unfilled, toggle to filled
        button.innerHTML = '★'; // Change to filled star
        button.classList.remove('unfilled');
        button.classList.add('filled');
        
        // Optionally, save the image
    }
    toggleSave(imageId)
}
function toggleSave(imageId) {
    fetch('/save-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_id: imageId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status == "success") {
            console.log('Image saved successfully!');
            window.location.reload()
        } else {
            console.log('Failed to save image');
        }
    })
    .catch(error => console.error('Error:', error));
}

function saveImageFromURL() {
    const imageUrl = document.getElementById("download-link").href
    console.log("image_url trying to save: " + imageUrl)
    fetch('/save-image-by-url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_url: imageUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status == "success") {
            alert('Image saved successfully!');
        } else {
            alert('Failed to save image');
        }
    })
    .catch(error => console.error('Error:', error));
}