import requests
from PIL import Image
from io import BytesIO
import os
import time

api_key = "rpooOfLYqrqk7kvuGa8utg"
save_folder = r"E:\Jarvis_Images"
os.makedirs(save_folder, exist_ok=True)

while True:
    try:
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            data = f.read().strip()

        prompt, status = data.split(",")
        if status.strip().lower() == "true":
            print(f"🤖 Jarvis: Prompt received — \"{prompt}\"")
            
            json_payload = {
                "prompt": prompt,
                "params": {
                    "n": 1,
                    "width": 512,
                    "height": 512,
                    "steps": 20
                }
            }

            headers = {
                "apikey": api_key,
                "Client-Agent": "JarvisAI/1.0"
            }

            print("📡 Sending request to Stable Horde...")
            res = requests.post("https://stablehorde.net/api/v2/generate/async", json=json_payload, headers=headers)

            if res.status_code == 202:
                job_id = res.json()["id"]
                print("🕒 Job started:", job_id)

                while True:
                    time.sleep(2)
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}").json()

                    if status.get("done"):
                        print("✅ Image ready, downloading...")

                        img_url = status["generations"][0]["img"]
                        img_data = requests.get(img_url).content
                        img = Image.open(BytesIO(img_data))

                        filename = f"{prompt.replace(' ', '_')}.png"
                        path = os.path.join(save_folder, filename)
                        img.save(path)
                        img.show()

                        print("✅ Image saved at:", path)

                        with open("Frontend/Files/ImageGeneration.data", "w") as f:
                            f.write("False, False")
                        break
                    else:
                        print("⌛ Waiting for image...")
            else:
                print(f"❌ Error {res.status_code}: {res.text}")

        else:
            time.sleep(1)

    except Exception as e:
        print("⚠️ Jarvis Error:", e)
        time.sleep(2)
