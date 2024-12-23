const socket = io();

const activeUsersList = document.getElementById('active-users-list');
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

// Fetch active users and join a chat
socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('join');
});

// Display active users
socket.on('active_users', (users) => {
    activeUsersList.innerHTML = '';
    users.forEach((user) => {
        const li = document.createElement('li');
        li.textContent = user;
        activeUsersList.appendChild(li);
    });
});

// Display system messages (e.g., chat assignment)
socket.on('system_message', (message) => {
    displayMessage('System', message);
});

// Display chat messages
socket.on('chat_message', (data) => {
    displayMessage(data.sender, data.message);
});

// Send message to server
sendButton.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') sendMessage();
});

function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        socket.emit('message', { message });
        displayMessage('You', message); // Show the user's own message locally
        chatInput.value = '';
    }
}

function displayMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = `${sender}: ${message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
