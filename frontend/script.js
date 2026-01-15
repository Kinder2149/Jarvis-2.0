const input = document.getElementById("user-input");
const button = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const messagesDiv = document.getElementById("messages");

let isSending = false;
function setLoading(loading) {
    isSending = loading;
    button.disabled = loading;
    input.disabled = loading;
    button.textContent = loading ? "Envoi..." : "Envoyer";
}

function getSessionId() {
    let id = localStorage.getItem("jarvis_session_id");
    if (!id) {
        // simple UUID v4-ish using crypto API
        id = ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
        localStorage.setItem("jarvis_session_id", id);
    }
    return id;
}

function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.innerText = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

button.onclick = async () => {
    if (isSending) return;
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
        setLoading(true);
        const res = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: getSessionId() })
        });

        const data = await res.json();
        addMessage(data.response, "ai");
    } catch {
        addMessage("Erreur de connexion au backend.", "ai");
    } finally {
        setLoading(false);
    }
};

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        button.click();
    }
});

newChatBtn.onclick = () => {
    localStorage.removeItem("jarvis_session_id");
    messagesDiv.innerHTML = "";
    addMessage("Nouvelle conversation démarrée.", "ai");
};