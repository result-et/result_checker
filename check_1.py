import requests
from bs4 import BeautifulSoup
import json
import time

URL = "https://corporate.ethiopianairlines.com/AboutEthiopian/careers/results"  # replace if needed
BOT_TOKEN = "8781730368:AAE6SGnocTysJaBG2K0X8GJZh4NTKB3dddw"
CHAT_ID = "727744944"

KEYWORDS = ["A/C MAINTENANCE TECHNICIAN", "PILOT"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
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
#         for keyword in KEYWORDS:
#             if keyword.lower() in r.lower():
#                 filtered.append(r)
#                 break
#     return filtered

def filter_amt(results):
    filtered = []
    for r in results:
        if all(keyword.lower() in r.lower() for keyword in KEYWORDS):
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
    while True:
        main()
        time.sleep(20)  # every 1 minute