document.addEventListener('DOMContentLoaded', () => {
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.querySelector('.chat-messages');

    // --- Event Listeners ---
    chatToggle.addEventListener('click', () => {
        // Use flex instead of block to respect the CSS layout
        chatWidget.style.display = 'flex';
        chatToggle.style.display = 'none';
    });

    chatCloseBtn.addEventListener('click', () => {
        chatWidget.style.display = 'none';
        chatToggle.style.display = 'flex';
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        chatInput.value = '';

        try {
            const response = await fetch('/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Note: CSRF token is not needed due to csrf_exempt on the view,
                    // but in a more secure setup, you'd fetch and send the token.
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            addMessage(data.reply, 'assistant');
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage(`Error: ${error.message}`, 'assistant');
        }
    });

    // --- Helper Functions ---
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', `${role}-message`);
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        // Scroll to the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
