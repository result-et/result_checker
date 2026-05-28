import requests
from bs4 import BeautifulSoup
import json
import time

URL = "https://corporate.ethiopianairlines.com/AboutEthiopian/careers/results"  # replace if needed
BOT_TOKEN = "8781730368:AAE6SGnocTysJaBG2K0X8GJZh4NTKB3dddw"
# CHAT_ID = "727744944"



KEYWORDS = [
    ["A/C MAINTENANCE TECHNICIAN", "AMT", "Pilot", "PTS"],
    ["ADDIS ABABA", "Region"]
]

USERS_FILE = "users.json"

# ---------------- USERS ---------------- #

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def add_user(chat_id):
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        save_users(users)

# ----------------NEW SUB ---------------#

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    return requests.get(url, params=params).json()


def handle_updates(offset=None):
    updates = get_updates(offset)

    for update in updates.get("result", []):
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if text == "/start":
            add_user(chat_id)
            send_welcome(chat_id)

    if updates["result"]:
        return updates["result"][-1]["update_id"] + 1

    return offset

def send_welcome(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": chat_id,
        "text": "✅ You will receive AMT updates."
    })
# ---------------------------------------#

# def send_telegram(message):
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     data = {
#         "chat_id": CHAT_ID,
#         "text": message
#     }
#     requests.post(url, data=data)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    users = load_users()

    for chat_id in users:
        data = {
            "chat_id": chat_id,
            "text": message
        }
        requests.post(url, data=data)

def fetch_results():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    cards = soup.find_all("div", class_="card")

    for card in cards:
        header = card.find("div", class_="card-header")
        if not header:
            continue

        text = header.get_text(separator=" ", strip=True)

        results.append(text)

    return results

# def filter_amt(results):
#     filtered = []
#     for r in results:
#         if all(keyword.lower() in r.lower() for keyword in KEYWORDS):
#             filtered.append(r)
#     return filtered

def filter_amt(results):
    filtered = []

    for r in results:
        if all(
            any(keyword.lower() in r.lower() for keyword in group)
            for group in KEYWORDS
        ):
            filtered.append(r)

    return filtered

def load_old():
    try:
        with open("seen.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_new(data):
    with open("seen.json", "w") as f:
        json.dump(data, f)

def main():
    print("Checking for AMT updates...")

    results = fetch_results()
    amt_results = filter_amt(results)

    old_results = load_old()

    new_posts = [r for r in amt_results if r not in old_results]

    if new_posts:
        for post in new_posts:
            message = f"✈️ New Result Posted:\n\n{post}"
            send_telegram(message)
            print("New:", post)

        save_new(amt_results)
    else:
        print("No new AMT updates.")

if __name__ == "__main__":
    offset = None


    offset = handle_updates(offset)
    main()
        