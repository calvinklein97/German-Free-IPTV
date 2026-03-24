import re
import requests
import urllib.parse

URL = "https://iptv-org.github.io/iptv/languages/deu.m3u"

response = requests.get(URL)
content = response.text

lines = content.splitlines()

output = []

for line in lines:
    if line.startswith("#EXTINF"):
        parts = line.split(",", 1)
        name = parts[1].strip()

        # dein Logo-Link
        logo_url = f"https://raw.githubusercontent.com/calvinklein97/German-Free-IPTV/main/logos/{name}.PNG"

        if 'tvg-logo="' in parts[0]:
            parts[0] = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', parts[0])
        else:
            parts[0] += f' tvg-logo="{logo_url}"'

        line = parts[0] + "," + name

    output.append(line)

with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
