// ========================================
// ABRARAI - MAIN JAVASCRIPT
// ========================================


// ========================================
// TYPING TEXT
// ========================================

const typingText = "Your personal AI system is ready...";
const typingElement = document.getElementById("typing");

let index = 0;

function typeText() {
    if (!typingElement) {
        return;
    }

    if (index < typingText.length) {
        typingElement.textContent += typingText[index];
        index++;

        setTimeout(typeText, 50);
    }
}

typeText();


// ========================================
// LIVE CLOCK
// ========================================

function updateClock() {
    const now = new Date();

    const time = now.toLocaleTimeString();

    const clock = document.getElementById("clock");

    if (clock) {
        clock.textContent = time;
    }
}

updateClock();

setInterval(updateClock, 1000);


// ========================================
// START SYSTEM BUTTON
// ========================================

function startAI() {
    const terminal = document.getElementById("terminalText");

    if (terminal) {
        terminal.innerHTML = `
            > Starting AbrarAI system...<br>
            > Connecting AI brain...<br>
            > Checking network...<br>
            > Loading intelligence modules...<br>
            > Security check passed.<br>
            > System initialization complete.<br>
            > AI brain is online.<br>
            > <strong>ABRARAI IS READY 🚀</strong>
        `;
    }

    alert("🚀 ABRARAI SYSTEM STARTED!");
}


// ========================================
// AI CHAT
// ========================================

async function sendMessage() {

    const input = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatMessages");

    if (!input || !chatBox) {
        return;
    }

    const message = input.value.trim();

    if (!message) {
        return;
    }


    // USER MESSAGE

    const userMessage = document.createElement("div");

    userMessage.className = "user-message";

    userMessage.textContent = message;

    chatBox.appendChild(userMessage);


    // CLEAR INPUT

    input.value = "";


    // AI THINKING MESSAGE

    const aiMessage = document.createElement("div");

    aiMessage.className = "ai-message";

    aiMessage.textContent = "AbrarAI is thinking...";

    chatBox.appendChild(aiMessage);


    // SCROLL

    chatBox.scrollTop = chatBox.scrollHeight;


    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        if (data.reply) {

            aiMessage.textContent = data.reply;

        } else {

            aiMessage.textContent =
                "Sorry Sir, I could not generate a response.";

        }


    } catch (error) {

        console.error("Chat error:", error);

        aiMessage.textContent =
            "❌ Unable to connect to AbrarAI.";

    }


    // SCROLL AGAIN

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ========================================
// ENTER KEY FOR CHAT
// ========================================

function handleChatKey(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }
}


// ========================================
// SYSTEM STATUS
// ========================================

async function updateSystemStatus() {

    try {

        const response = await fetch("/api/system");

        const data = await response.json();


        // CPU

        const cpu = document.getElementById("cpu");

        if (cpu && data.cpu !== undefined) {
            cpu.textContent = data.cpu + "%";
        }


        // RAM

        const ram = document.getElementById("ram");

        if (ram && data.ram) {
            ram.textContent =
                data.ram.percent + "%";
        }


        // DISK

        const disk = document.getElementById("disk");

        if (disk && data.disk) {
            disk.textContent =
                data.disk.percent + "%";
        }


        // AI ENGINE

        const aiEngine =
            document.getElementById("aiEngine");

        if (aiEngine) {

            aiEngine.textContent =
                data.ai_engine || "OFFLINE";

        }


        // MODEL

        const model =
            document.getElementById("model");

        if (model) {

            model.textContent =
                data.model || "Unknown";

        }


        // SERVER

        const server =
            document.getElementById("server");

        if (server) {

            server.textContent =
                data.server
                    ? "ONLINE"
                    : "OFFLINE";

        }


        // REQUESTS

        const requests =
            document.getElementById("requests");

        if (requests) {

            requests.textContent =
                data.requests || 0;

        }


        // RESPONSE TIME

        const responseTime =
            document.getElementById("responseTime");

        if (responseTime) {

            responseTime.textContent =
                (data.response_time || 0) + "s";

        }


    } catch (error) {

        console.error(
            "System status error:",
            error
        );

    }
}


// ========================================
// START SYSTEM MONITOR
// ========================================

updateSystemStatus();

setInterval(
    updateSystemStatus,
    3000
);


// ========================================
// MAKE FUNCTIONS AVAILABLE TO HTML
// ========================================

window.startAI = startAI;

window.sendMessage = sendMessage;

window.handleChatKey = handleChatKey;