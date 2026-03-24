import re
import requests
import urllib.parse

BASE_URL = "https://raw.githubusercontent.com/calvinklein97/German-Free-IPTV/main/Logos/"

def get_logo_url(name):
    """Versucht .PNG und .png und gibt die funktionierende URL zurück."""
    for ext in [".PNG", ".png"]:
        url = BASE_URL + urllib.parse.quote(name + ext)
        try:
            r = requests.head(url)
            if r.status_code == 200:
                return url
        except requests.RequestException:
            continue
    return ""  # kein Logo gefunden

# M3U einlesen
URL = "https://iptv-org.github.io/iptv/languages/deu.m3u"
content = requests.get(URL).text
lines = content.splitlines()

output = []

for line in lines:
    if line.startswith("#EXTINF"):
        parts = line.split(",", 1)
        name = parts[1].strip()
        logo_url = get_logo_url(name)

        if 'tvg-logo="' in parts[0]:
            parts[0] = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', parts[0])
        else:
            parts[0] += f' tvg-logo="{logo_url}"'

        line = parts[0] + "," + name

    output.append(line)

# Output schreiben
with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
