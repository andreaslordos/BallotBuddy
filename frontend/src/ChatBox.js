import React, { useState } from "react";
import './ChatBox.css';
import ReactMarkdown from 'react-markdown';  // Import react-markdown

function ChatBox() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = (e) => {
        e.preventDefault();

        if (!input.trim() || input.length < 3) {
            return;
        }
    
        const userMessage = {
            user: "You",
            type: "text",
            content: input
        };
    
        setMessages(prevMessages => [userMessage, ...prevMessages]);
    
        setIsLoading(true);
    
        fetch(`http://127.0.0.1:5601/query?text=${input}`)
            .then((response) => response.json())  // Parsing as JSON
            .then((data) => {
                const newMessages = data.map(item => {
                    let messageContent = item;
    
                    return {
                        user: "Bot",
                        content: messageContent
                    };
                });
    
                setMessages(prevMessages => [...newMessages, ...prevMessages]);
                setIsLoading(false);
            })
            .catch((error) => {
                console.error("Error:", error);
                setIsLoading(false);
            });
    
        setInput("");
    };
    // <img src='image.png' alt="Sent by bot" />

    return (
        <div className={`chatbox ${messages.length > 0 ? 'has-messages' : ''}`}>
            <div className="messages">
                {[...messages].reverse().map((message, idx) => (
                    <div key={idx} className={`message ${message.user.toLowerCase()}`}>
                        {message.content === "image" ? (
                            <ReactMarkdown>"this is supposed to be an image"</ReactMarkdown>
                        ) : (
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                        )}
                    </div>
                ))}
            </div>
            <form className="input-area" onSubmit={handleSend}>
                <input
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Type your message..."
                />
                <button type="submit" disabled={isLoading || !input.trim() || input.length < 3}>
                    Send
                </button>
            </form>
        </div>
    );
}

export default ChatBox;
