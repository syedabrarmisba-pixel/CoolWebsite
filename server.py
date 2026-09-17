from flask import Flask, request, jsonify, send_file
import os
import time
import psutil
from datetime import datetime
from groq import Groq

app = Flask(__name__)

# ==============================
# GROQ AI SETTINGS
# ==============================

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-20b"

client = None

if API_KEY:
    client = Groq(api_key=API_KEY)


# ==============================
# STATISTICS
# ==============================

ai_requests = 0
last_response_time = 0
activity_log = []


# ==============================
# ACTIVITY LOG
# ==============================

def add_activity(message):
    current_time = datetime.now().strftime("%H:%M:%S")

    activity_log.insert(
        0,
        {
            "time": current_time,
            "message": message
        }
    )

    del activity_log[10:]


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return send_file("index.html")


# ==============================
# SYSTEM STATUS
# ==============================

@app.route("/api/system")
def system_stats():

    try:
        cpu = psutil.cpu_percent(interval=0.1)

        memory = psutil.virtual_memory()

        disk = psutil.disk_usage(os.path.abspath(os.sep))

        ai_online = client is not None

        return jsonify(
            {
                "cpu": round(cpu, 1),

                "ram": {
                    "percent": round(memory.percent, 1),
                    "used": round(memory.used / (1024 ** 3), 1),
                    "total": round(memory.total / (1024 ** 3), 1)
                },

                "disk": {
                    "percent": round(disk.percent, 1),
                    "used": round(disk.used / (1024 ** 3), 1),
                    "total": round(disk.total / (1024 ** 3), 1)
                },

                "ollama": ai_online,

                "model": MODEL,

                "server": True,

                "time": datetime.now().strftime("%H:%M:%S"),

                "ai_engine": "ONLINE" if ai_online else "OFFLINE",

                "connection": (
                    "CONNECTED"
                    if ai_online
                    else "API KEY MISSING"
                ),

                "requests": ai_requests,

                "response_time": round(
                    last_response_time,
                    2
                ),

                "activity": activity_log
            }
        )

    except Exception as error:

        print("SYSTEM ERROR:", error)

        return jsonify(
            {
                "server": True,
                "ollama": False,
                "ai_engine": "OFFLINE",
                "connection": "ERROR",
                "requests": ai_requests,
                "response_time": round(
                    last_response_time,
                    2
                ),
                "activity": activity_log
            }
        ), 500


# ==============================
# AI CHAT
# ==============================

@app.route("/api/chat", methods=["POST"])
def chat():

    global ai_requests
    global last_response_time

    start_time = time.time()

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify(
                {
                    "reply": "Please send a message."
                }
            ), 400

        message = str(
            data.get("message", "")
        ).strip()

        if not message:

            return jsonify(
                {
                    "reply": "Please type a message."
                }
            ), 400

        ai_requests += 1

        add_activity(
            "AI request received"
        )

        # ==============================
        # CHECK API KEY
        # ==============================

        if client is None:

            add_activity(
                "ERROR: Groq API key missing"
            )

            return jsonify(
                {
                    "reply": "AI is not configured. Please check GROQ_API_KEY."
                }
            ), 500

        # ==============================
        # SIMPLE GREETINGS
        # ==============================

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

            return jsonify(
                {
                    "reply": "Hello Sir! 👋 How can I help you?",

                    "response_time": round(
                        last_response_time,
                        2
                    )
                }
            )

        # ==============================
        # GROQ PROCESSING
        # ==============================

        add_activity(
            "Groq AI processing request"
        )

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are AbrarAI, a helpful AI assistant. "
                        "Answer the user's actual question directly. "
                        "Be accurate and concise. "
                        "Use simple English or Hinglish when appropriate. "
                        "Do not invent personal information."
                    )
                },

                {
                    "role": "user",
                    "content": message
                }
            ],

            temperature=0.4,

            max_tokens=500
        )

        # ==============================
        # GET AI RESPONSE
        # ==============================

        reply = response.choices[0].message.content

        if reply is None:
            reply = ""

        reply = reply.strip()

        last_response_time = (
            time.time() - start_time
        )

        if not reply:

            reply = (
                "Sorry Sir, I could not generate a response."
            )

        add_activity(
            "AI response generated"
        )

        return jsonify(
            {
                "reply": reply,

                "response_time": round(
                    last_response_time,
                    2
                )
            }
        )

    except Exception as error:

        last_response_time = (
            time.time() - start_time
        )

        print(
            "AI ERROR:",
            error
        )

        add_activity(
            "ERROR: AI request failed"
        )

        return jsonify(
            {
                "reply": (
                    "AI request failed. "
                    "Please try again."
                ),

                "response_time": round(
                    last_response_time,
                    2
                )
            }
        ), 500


# ==============================
# START SERVER
# ==============================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "          ABRARAI"
    )

    print(
        "================================"
    )

    if API_KEY:
        print(
            "AI Engine: GROQ ONLINE"
        )
    else:
        print(
            "AI Engine: API KEY MISSING"
        )

    print(
        "Model:",
        MODEL
    )

    print(
        "Server: ON"
    )

    print(
        "System Monitor: ON"
    )

    print(
        "Open: http://127.0.0.1:5000"
    )

    print(
        "================================"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )