from dotenv import dotenv_values
import os
import mtranslate as mt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# ---------------- ENV ----------------
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

# ---------------- PATH ----------------
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "Data")
TEMP_DIR = os.path.join(BASE_DIR, "Frontend", "Files")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

HTML_PATH = os.path.join(DATA_DIR, "Voice.html")

# ---------------- HTML ----------------
HtmlCode = f""" 
<!DOCTYPE html>
<html>
<head>
<title>Speech Recognition</title>
</head>
<body>

<button id="start">Start</button>
<p id="output"></p>

<script>
const output = document.getElementById("output");

let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false;   // 🔥 FIX
recognition.lang = "{InputLanguage}";

document.getElementById("start").onclick = () => recognition.start();

recognition.onresult = function(event) {{
    const transcript = event.results[0][0].transcript;
    output.textContent = transcript;
    recognition.stop();
}};
</script>

</body>
</html>
"""

# Save HTML
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# ---------------- DRIVER ----------------
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")

    driver_path = os.path.join(BASE_DIR, "chromedriver.exe")

    if not os.path.exists(driver_path):
        raise Exception("❌ chromedriver.exe NOT FOUND in project folder")

    return webdriver.Chrome(
        service=Service(driver_path),
        options=chrome_options
    )

# ---------------- STATUS ----------------
def SetAssistantStatus(status):
    try:
        with open(os.path.join(TEMP_DIR, "Status.data"), "w") as f:
            f.write(status)
    except:
        pass

# ---------------- TRANSLATE ----------------
def UniversalTranslator(text):
    try:
        return mt.translate(text, "en", "auto").capitalize()
    except:
        return text

# ---------------- SPEECH ----------------
def SpeechRecognition():
    driver = None

    try:
        print("🎤 Listening...")
        SetAssistantStatus("Listening...")

        driver = create_driver()
        driver.get(f"file:///{HTML_PATH.replace(os.sep, '/')}")

        time.sleep(1)
        driver.find_element(By.ID, "start").click()

        timeout = time.time() + 10

        while True:
            time.sleep(0.5)

            text = driver.find_element(By.ID, "output").get_attribute("innerText").strip()

            if text:
                print("✅ YOU SAID:", text)

                driver.quit()
                SetAssistantStatus("Processing...")
                return UniversalTranslator(text)

            if time.time() > timeout:
                driver.quit()
                SetAssistantStatus("Available...")
                return ""

    except Exception as e:
        print("❌ Speech Error:", e)

        if driver:
            driver.quit()

        return ""

# ---------------- TEST ----------------
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print("YOU SAID:", result)

        if "stop" in result.lower():
            break