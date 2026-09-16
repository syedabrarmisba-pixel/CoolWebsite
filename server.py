from flask import Flask, request, jsonify, send_file
import requests
import psutil
import os
import time
from datetime import datetime

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"

MODEL = "tinyllama:latest"

# =========================
# AI ACTIVITY
# =========================

ai_requests = 0
last_response_time = 0
activity_log = []

server_start_time = time.time()


def add_activity(message):

    global activity_log

    current_time = datetime.now().strftime("%H:%M:%S")

    activity_log.insert(
        0,
        {
            "time": current_time,
            "message": message
        }
    )

    activity_log = activity_log[:15]


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return send_file("index.html")


# =========================
# SYSTEM MONITOR
# =========================

@app.route("/api/system")
def system_stats():

    try:

        # CPU
        cpu = psutil.cpu_percent(interval=0.1)

        # RAM
        memory = psutil.virtual_memory()

        ram_percent = memory.percent
        ram_used = memory.used / (1024 ** 3)
        ram_total = memory.total / (1024 ** 3)

        # STORAGE
        disk = psutil.disk_usage(
            os.path.abspath(os.sep)
        )

        disk_percent = disk.percent
        disk_used = disk.used / (1024 ** 3)
        disk_total = disk.total / (1024 ** 3)

        # OLLAMA
        ollama_online = False

        try:

            ollama_response = requests.get(
                OLLAMA_TAGS_URL,
                timeout=3
            )

            if ollama_response.status_code == 200:
                ollama_online = True

        except requests.exceptions.RequestException:

            ollama_online = False

        # UPTIME
        uptime_seconds = int(
            time.time() - server_start_time
        )

        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

        uptime = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        # TIME
        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        return jsonify({

            "cpu": round(cpu, 1),

            "ram": {
                "percent": round(
                    ram_percent,
                    1
                ),
                "used": round(
                    ram_used,
                    1
                ),
                "total": round(
                    ram_total,
                    1
                )
            },

            "disk": {
                "percent": round(
                    disk_percent,
                    1
                ),
                "used": round(
                    disk_used,
                    1
                ),
                "total": round(
                    disk_total,
                    1
                )
            },

            "ollama": ollama_online,

            "model": MODEL,

            "server": True,

            "time": current_time,

            "uptime": uptime,

            "ai_engine":
                "ONLINE"
                if ollama_online
                else "OFFLINE",

            "connection":
                "CONNECTED",

            "requests":
                ai_requests,

            "response_time":
                round(
                    last_response_time,
                    2
                ),

            "activity":
                activity_log

        })

    except Exception as e:

        print(
            "SYSTEM MONITOR ERROR:",
            e
        )

        return jsonify({

            "server": True,

            "ollama": False,

            "ai_engine": "OFFLINE",

            "connection": "ERROR",

            "requests":
                ai_requests,

            "response_time":
                round(
                    last_response_time,
                    2
                ),

            "uptime":
                "ERROR",

            "activity":
                activity_log,

            "error":
                "Could not read system information."

        }), 500


# =========================
# AI CHAT
# =========================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    global ai_requests
    global last_response_time

    start_time = time.time()

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "reply":
                "Please send a message."
            })

        message = data.get(
            "message",
            ""
        ).strip()

        if not message:

            return jsonify({
                "reply":
                "Please type a message."
            })

        # =========================
        # REQUEST COUNT
        # =========================

        ai_requests += 1

        add_activity(
            "AI request received"
        )

        # =========================
        # GREETINGS
        # =========================

        greetings = {
            "hello",
            "hi",
            "hey",
            "salam",
            "salaam",
            "assalamualaikum",
            "assalamu alaikum"
        }

        if message.lower() in greetings:

            last_response_time = (
                time.time() - start_time
            )

            add_activity(
                "Greeting response generated"
            )

            return jsonify({

                "reply":
                "Hello Sir! 👋 How can I help you?",

                "response_time":
                round(
                    last_response_time,
                    2
                )

            })

        # =========================
        # AI PROCESSING
        # =========================

        add_activity(
            "AI processing request..."
        )

        prompt = f"""Answer this question directly.

Question:
{message}

Give only the answer.
Do not create another question.
Do not write "User question".
Do not write "Answer".
Do not create a conversation.
Do not pretend the user asked something else.

Response:"""

        response = requests.post(

            OLLAMA_URL,

            json={

                "model": MODEL,

                "prompt": prompt,

                "stream": False,

                "options": {

                    "temperature": 0.1,

                    "num_predict": 120

                }

            },

            timeout=120

        )

        response.raise_for_status()

        result = response.json()

        reply = result.get(
            "response",
            ""
        ).strip()

        # =========================
        # RESPONSE TIME
        # =========================

        last_response_time = (
            time.time() - start_time
        )

        # =========================
        # CLEAN RESPONSE
        # =========================

        unwanted = [

            "AbrarAI:",

            "ABRARAI:",

            "Answer:",

            "answer:",

            "Response:",

            "response:"

        ]

        for text in unwanted:

            if reply.startswith(text):

                reply = reply[
                    len(text):
                ].strip()

        # =========================
        # REMOVE FAKE QUESTIONS
        # =========================

        fake_question_markers = [

            "User question:",

            "User:",

            "Question:"

        ]

        for marker in fake_question_markers:

            if marker in reply:

                reply = reply.split(
                    marker
                )[0].strip()

        if not reply:

            reply = (
                "Sorry Sir, "
                "I couldn't generate "
                "a response."
            )

        add_activity(
            "AI response generated"
        )

        return jsonify({

            "reply": reply,

            "response_time":
                round(
                    last_response_time,
                    2
                )

        })

    # =========================
    # OLLAMA OFFLINE
    # =========================

    except requests.exceptions.ConnectionError:

        last_response_time = (
            time.time() - start_time
        )

        add_activity(
            "ERROR: Ollama offline"
        )

        return jsonify({

            "reply":
            "❌ Ollama is not running. "
            "Please start Ollama.",

            "response_time":
            round(
                last_response_time,
                2
            )

        }), 500

    # =========================
    # TIMEOUT
    # =========================

    except requests.exceptions.Timeout:

        last_response_time = (
            time.time() - start_time
        )

        add_activity(
            "ERROR: AI response timeout"
        )

        return jsonify({

            "reply":
            "❌ AI took too long "
            "to respond. Please try again.",

            "response_time":
            round(
                last_response_time,
                2
            )

        }), 500

    # =========================
    # REQUEST ERROR
    # =========================

    except requests.exceptions.RequestException as e:

        last_response_time = (
            time.time() - start_time
        )

        print(
            "OLLAMA ERROR:",
            e
        )

        add_activity(
            "ERROR: AI connection failed"
        )

        return jsonify({

            "reply":
            "❌ Could not connect "
            "to the AI.",

            "response_time":
            round(
                last_response_time,
                2
            )

        }), 500

    # =========================
    # GENERAL ERROR
    # =========================

    except Exception as e:

        last_response_time = (
            time.time() - start_time
        )

        print(
            "SERVER ERROR:",
            e
        )

        add_activity(
            "ERROR: Server error"
        )

        return jsonify({

            "reply":
            "❌ Something went wrong.",

            "response_time":
            round(
                last_response_time,
                2
            )

        }), 500


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    print()

    print(
        "================================"
    )

    print(
        "        🤖 ABRARAI"
    )

    print(
        "================================"
    )

    print(
        "AI Server: ON"
    )

    print(
        "System Monitor: ON"
    )

    print(
        "AI Activity Monitor: ON"
    )

    print(
        "Live Terminal: ON"
    )

    print(
        "System Events: ON"
    )

    print(
        "Uptime Monitor: ON"
    )

    print(
        "Request Counter: ON"
    )

    print(
        "Response Time Monitor: ON"
    )

    print(
        "Activity Log: ON"
    )

    print(
        "Model:",
        MODEL
    )

    print(
        "Open: "
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )