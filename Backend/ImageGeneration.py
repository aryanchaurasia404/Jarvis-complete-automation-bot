import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# ---------------- CONFIG ----------------
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

API_KEY = get_key(".env", "HuggingFaceAPIKey")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

DATA_DIR = "Data"
os.makedirs(DATA_DIR, exist_ok=True)

print("🔥 USING API:", API_URL)
print("🔑 API KEY LOADED:", "YES" if API_KEY else "NO")

# ---------------- OPEN IMAGES ----------------
def open_images(prompt):
    prompt = prompt.replace(" ", "_")

    for i in range(1, 5):
        path = os.path.join(DATA_DIR, f"{prompt}{i}.jpg")

        if not os.path.exists(path):
            print(f"❌ Missing: {path}")
            continue

        try:
            img = Image.open(path)
            print(f"🖼 Opening: {path}")
            img.show()
            sleep(1)
        except Exception as e:
            print(f"❌ Open Error: {e}")

# ---------------- API CALL ----------------
async def query(payload):
    try:
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print("❌ API ERROR:", response.status_code, response.text)
            return None

        # 🔥 IMPORTANT: image bytes directly
        if "image" in response.headers.get("content-type", ""):
            return response.content

        print("❌ Unexpected Response:", response.text[:200])
        return None

    except Exception as e:
        print("❌ Request Failed:", e)
        return None

# ---------------- GENERATE ----------------
async def generate_images(prompt: str):
    tasks = []

    clean_prompt = prompt.lower().replace("generate image", "").strip()

    for _ in range(4):
        payload = {
            "inputs": f"{clean_prompt}, ultra realistic, 4k, cinematic lighting",
            "parameters": {
                "seed": randint(0, 1000000)
            }
        }

        tasks.append(asyncio.create_task(query(payload)))

    results = await asyncio.gather(*tasks)

    for i, img_bytes in enumerate(results):
        if img_bytes is None:
            print(f"❌ Image {i+1} failed")
            continue

        file_path = os.path.join(DATA_DIR, f"{clean_prompt.replace(' ', '_')}{i+1}.jpg")

        try:
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            print(f"✅ Saved: {file_path}")
        except Exception as e:
            print(f"❌ Save Error: {e}")

# ---------------- WRAPPER ----------------
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ---------------- MAIN LOOP ----------------
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read().strip()

        if "," not in data:
            sleep(1)
            continue

        prompt, status = [x.strip() for x in data.split(",")]

        if status.lower() == "true":
            print("🚀 Generating Images...")

            GenerateImages(prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")

            break
        else:
            sleep(1)

    except Exception as e:
        print("❌ MAIN ERROR:"),