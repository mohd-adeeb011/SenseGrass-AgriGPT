// Declare chatHistory outside of the $(document).ready function
const chatHistory = $('#chat-history');

$(document).ready(function() {
    const sendButton = $('#send-button');
    const messageInput = $('#message-input');

    loadChatHistory();

    sendButton.click(function() {
        const message = messageInput.val().trim();
        if (message) {
            appendUserMessage(message); // Append user's message immediately
            messageInput.val('');
            sendMessage(message); // Send the message to the backend
        }
    });

    messageInput.keypress(function(e) {
        if (e.which == 13) { // Enter key
            sendButton.click();
        }
    });

    function appendUserMessage(message) {
        const userMessageElement = $('<p>').text(message).addClass('message user');
        chatHistory.append(userMessageElement);
        chatHistory.scrollTop(chatHistory[0].scrollHeight);
        saveChatHistory(); // Save chat history after appending a message
    }

    function sendMessage(message) {
        $.ajax({
            url: '/weather',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ user_prompt: message }),
            success: function(data) {

                
                // Split the response into lines
                const lines = data.response.split('\n');
                // Initialize an empty array to hold the formatted lines
                let formattedLines = [];
    
                // Iterate over each line
                lines.forEach(line => {
                    // Check if the line should be formatted as a bullet point
                    // This is a simple example; adjust the condition as needed
                    if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
                        // Wrap the line in <li> tags and trim whitespace
                        formattedLines.push(`<li>${line.trim().substring(1)}</li>`);
                    } else if (line.trim() !== '') {
                        // Append the line as is, but only if it's not empty
                        formattedLines.push(line.trim());
                    }
                });
    
                // Join the formatted lines with <br> tags to create a single string of HTML
                // Only insert <br> tags between lines that are not bullet points
                const responseHtml = formattedLines.join('<br>');
    
                // Directly insert the formatted HTML content into the DOM
                const responseElement = $('<div>').html(responseHtml).addClass('message response');
                chatHistory.append(responseElement);
                chatHistory.scrollTop(chatHistory[0].scrollHeight);
                saveChatHistory(); // Save chat history after appending a response
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    }

    $('#new-chat-button').click(function() {
        // Clear the chat history from the DOM
        chatHistory.empty();

        // Clear the chat history from localStorage
        localStorage.removeItem('chatHistory');

        // Reset any other state as needed
        // For example, resetting the message input field
        messageInput.val('');

        // Optionally, you can also redirect to the same page to ensure a clean state
        // window.location.reload();
    });
    
});

function saveChatHistory() {
    const messages = chatHistory.children().map(function() {
        return $(this).text();
    }).get();
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

function loadChatHistory() {
    const savedChatHistory = localStorage.getItem('chatHistory');
    if (savedChatHistory) {
        const messages = JSON.parse(savedChatHistory);
        messages.forEach(function(message, index) {
            // Determine if the message is a user message or a response
            // This is a simple example; you might need a more sophisticated method
            const isUserMessage = index % 2 === 0; // Assuming user messages are at even indices

            const messageElement = $('<p>').text(message);
            if (isUserMessage) {
                messageElement.addClass('message user');
            } else {
                messageElement.addClass('message response');
            }
            chatHistory.append(messageElement);
        });
    }
}

