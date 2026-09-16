const typingText = "Your personal AI system is ready...";
const typingElement = document.getElementById("typing");

let index = 0;

function typeText() {
if (index < typingText.length) {
typingElement.textContent += typingText[index];
index++;
setTimeout(typeText, 50);
}
}

typeText();

// LIVE CLOCK
function updateClock() {
const now = new Date();

```
const time = now.toLocaleTimeString();

const clock = document.getElementById("clock");

if (clock) {
    clock.textContent = time;
}
```

}

updateClock();
setInterval(updateClock, 1000);

// START SYSTEM BUTTON
function startAI() {

```
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
```

}
