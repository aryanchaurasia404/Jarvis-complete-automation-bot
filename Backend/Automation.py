# -------------------- IMPORTS --------------------
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from rich import print
from groq import Groq

import webbrowser
import subprocess
import keyboard
import asyncio
import os
from typing import List, Callable

# -------------------- CONFIG --------------------
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

DATA_DIR = "Data"
os.makedirs(DATA_DIR, exist_ok=True)

messages = []
SystemChatBot = [{"role": "system", "content": "You are a smart AI assistant that decides actions."}]

# -------------------- UTIL --------------------
def safe_execute(func: Callable, *args):
    try:
        return func(*args)
    except Exception as e:
        print(f"[ERROR] {func.__name__}: {e}")
        return None

# -------------------- BASIC ACTIONS --------------------
def GoogleSearch(topic: str):
    webbrowser.open(f"https://www.google.com/search?q={topic}")
    return True

def YouTubeSearch(topic: str):
    webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
    return True

def PlayYoutube(query: str):
    playonyt(query)
    return True

def OpenApp(app: str):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
    except:
        webbrowser.open(f"https://www.google.com/search?q={app}")
    return True

def CloseApp(app: str):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False
def Content(topic: str):
    file_path = os.path.join(DATA_DIR, f"{topic.replace(' ', '_')}.txt")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # ✅ updated model
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": topic}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    answer = completion.choices[0].message.content

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(answer)

    subprocess.Popen(["notepad.exe", file_path])

    return True

def System(command: str):
    actions = {
        "mute": "volume mute",
        "unmute": "volume mute",
        "volume up": "volume up",
        "volume down": "volume down"
    }

    for key in actions:
        if key in command:
            keyboard.press_and_release(actions[key])
            return True

    return False

# -------------------- AI DECISION ENGINE --------------------
def DecideIntent(command: str):

    command = command.lower()

    if any(x in command for x in ["open", "start", "launch"]):
        return "open"

    elif any(x in command for x in ["close", "stop"]):
        return "close"

    elif any(x in command for x in ["play", "song", "youtube"]):
        return "play"

    elif any(x in command for x in ["search", "google"]):
        return "google"

    elif any(x in command for x in ["write", "application", "essay", "content"]):
        return "content"

    elif any(x in command for x in ["volume", "mute"]):
        return "system"

    else:
        return "unknown"

# -------------------- EXECUTOR --------------------
async def TranslateAndExecute(commands: List[str]):

    tasks = []

    for command in commands:

        intent = DecideIntent(command)

        if intent == "open":
            tasks.append(asyncio.to_thread(OpenApp, command))

        elif intent == "close":
            tasks.append(asyncio.to_thread(CloseApp, command))

        elif intent == "play":
            tasks.append(asyncio.to_thread(PlayYoutube, command))

        elif intent == "google":
            tasks.append(asyncio.to_thread(GoogleSearch, command))

        elif intent == "content":
            tasks.append(asyncio.to_thread(Content, command))

        elif intent == "system":
            tasks.append(asyncio.to_thread(System, command))

        else:
            print(f"[AI] I don't understand: {command}")

    if tasks:
        results = await asyncio.gather(*tasks)

        for r in results:
            yield r

# -------------------- MAIN LOOP --------------------
async def Automation(commands: List[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True


# -------------------- RUN --------------------
if __name__ == "__main__":
    while True:
        user_input = input("Ask Jarvis: ")

        if user_input.lower() == "exit":
            break

        asyncio.run(Automation([user_input]))