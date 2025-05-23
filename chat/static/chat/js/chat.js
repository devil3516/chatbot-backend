document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const chatLoading = document.getElementById('chatLoading');
    const chatError = document.getElementById('chatError');
    const sendButton = document.getElementById('sendButton');

    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add message to chat
    function addMessage(content, sender, isHTML = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        if (isHTML) {
            messageDiv.innerHTML = content;
        } else {
            messageDiv.textContent = content;
        }
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle form submit
    async function handleSubmit(e) {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        userInput.disabled = true;
        sendButton.disabled = true;

        addMessage(message, 'user');
        userInput.value = '';

        chatLoading.style.display = 'flex';
        chatError.style.display = 'none';

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            let formattedResponse = '';

let responseText = '';
if (Array.isArray(data.response)) {
    responseText = data.response[0];  // extract the string part
} else if (typeof data.response === 'string') {
    responseText = data.response;
}

if (typeof responseText === 'string') {
    // Format newlines and preserve Markdown-like bold/italics/code formatting
    formattedResponse = responseText
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')   // code blocks
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')             // bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')                         // italics
        .replace(/`([^`]+)`/g, '<code>$1</code>')                     // inline code
        .replace(/\n/g, '<br>');                                      // line breaks
} else {
    formattedResponse = 'Unexpected response format.';
}


            addMessage(formattedResponse, 'assistant', true);

        } catch (error) {
            console.error('Error:', error);
            chatError.style.display = 'block';
            chatError.textContent = 'An error occurred. Please try again.';
        } finally {
            userInput.disabled = false;
            sendButton.disabled = false;
            chatLoading.style.display = 'none';
            userInput.focus();
        }
    }

    chatForm.addEventListener('submit', handleSubmit);

    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    userInput.focus();
});

/**
 * Chat functionality:
 * - Message submission handling
 * - Fetch API for Groq requests
 * - Dynamic message display
 * - Loading states
 * - Error handling
 * - Auto-scrolling
 * - Textarea resizing
 */
