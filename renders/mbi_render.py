#!/usr/bin/env python3
"""
MBI Mebel - avtomatik fotorealistik render skripti
Ishlatish: python3 mbi_render.py <rasm_yo'li> <api_key> [prompt]
Talab: api.myarchitectai.com va ik.imagekit.io ruxsat etilgan bo'lishi kerak.
"""
import sys, json, base64, time, urllib.request

GITHUB_TOKEN = None  # ixtiyoriy: rasmni GitHub orqali hosting qilish uchun
REPO = "yakubovibrohim/MBI_anketa"

DEFAULT_PROMPT = ("photorealistic interior photography of a classic luxury kitchen, "
    "white painted classic panel cabinets with moldings, dark emperador brown marble "
    "countertop and backsplash with golden veins, black built-in appliances, "
    "oak wood floor, warm natural daylight, soft shadows, "
    "professional architectural photography, 4k, highly detailed")

def gh_upload(path, token):
    name = f"renders/auto_{int(time.time())}.png"
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{name}",
        data=json.dumps({"message": "auto render upload", "content": b64}).encode(),
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"},
        method="PUT")
    with urllib.request.urlopen(req) as r:
        return json.load(r)["content"]["download_url"]

def render(image_url, api_key, prompt, endpoint="interior"):
    req = urllib.request.Request(
        f"https://api.myarchitectai.com/v1/render/{endpoint}",
        data=json.dumps({"image": image_url, "outputFormat": "jpg", "prompt": prompt}).encode(),
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def upscale(image_url, api_key):
    req = urllib.request.Request(
        "https://api.myarchitectai.com/v1/upscale-4k",
        data=json.dumps({"image": image_url, "outputFormat": "jpg"}).encode(),
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)

if __name__ == "__main__":
    img, key = sys.argv[1], sys.argv[2]
    prompt = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PROMPT
    url = img if img.startswith("http") else gh_upload(img, GITHUB_TOKEN)
    print("Input:", url)
    res = render(url, key, prompt)
    out = res.get("output") or res
    print("Natija:", out)
    if isinstance(out, str):
        urllib.request.urlretrieve(out, "/mnt/user-data/outputs/realistik_natija.jpg")
        print("Saqlandi: /mnt/user-data/outputs/realistik_natija.jpg")
