import json
from bot import Archiver

# ---------------- SETUP ----------------

token = None

with open("./secret.json", "r") as secret:
    try:
        data = json.load(secret)
        print(data)
        token = data["token"]
    except Exception as e:
        print(f'Failed to read JSON data, provided error: {e}')

bot = Archiver()
bot.run(token)
