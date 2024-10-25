let selectedImageId = null;
let selectedUser = null;

function openShareModal(imageId) {
    selectedImageId = imageId
    console.log("image picked: " + selectedImageId)
    document.getElementById("share-modal").style.display = "block"
}


function closeShareModal() {
    document.getElementById("share-modal").style.display = "none"
}

function searchUsers() {
    const query = document.getElementById("userSearchInput").value;

    fetch("/get_all_users", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        users = data;
        console.log("all users: " + users);

        const filteredUsers = users.filter(user => 
            user.username.toLowerCase().includes(query.toLowerCase()
        ));
        console.log("filtered:  " + filteredUsers)
        
        const userResultsList = document.getElementById('userResults');
        userResultsList.innerHTML = ''; // Clear 
    
        filteredUsers.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user.username;
            li.onclick = () => selectUser(user);
            userResultsList.appendChild(li);
        });
    })    
    .catch(error => console.error("Error fetching users", error));

}

let selectedUserId = null;

function selectUser(user) {
    selectedUserId = user.id;
    alert(`Selected user: ${user.username}, id: ${user.id}`);
}

function sendImageToUser() {
    if (!selectedUserId) {
        alert('Please select a user.');
        return;
    }

    const data = {
        receiver_user_id: selectedUserId,  // The selected user ID
        image_id: selectedImageId // The selected image ID
    };

    fetch("/share-image", {
        method: "POST",         
        headers: {
            "Content-Type": "application/json", 
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())  
    .then(result => {
        if (result.status == "success") {
            console.log("Image sent successfully!");
        } else {
            console.log("Failed to send image.");
        }
    })
    .catch(error => {
        console.error("Error sending image:", error);
        alert("An error occurred while trying to share an image.");
    });
}