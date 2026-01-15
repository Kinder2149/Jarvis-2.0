const input = document.getElementById("user-input");
const button = document.getElementById("send-btn");
const messagesDiv = document.getElementById("messages");

function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.innerText = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

button.onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
        const res = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        addMessage(data.response, "ai");
    } catch {
        addMessage("Erreur de connexion au backend.", "ai");
    }
};