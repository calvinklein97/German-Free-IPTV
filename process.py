import re
import requests

# --- Einstellungen ---
BASE_URL = "https://raw.githubusercontent.com/calvinklein97/German-Free-IPTV/main/Logos/"
M3U_URL = "https://iptv-org.github.io/iptv/languages/deu.m3u"
OUTPUT_FILE = "output.m3u"

# --- Hilfsfunktionen ---
def sanitize_filename(name):
    """
    Wandelt Namen in gültige GitHub-Logodateinamen um:
    - Entfernt nur problematische Zeichen wie /
    - Umlaute bleiben unverändert
    """
    name = name.replace("/", "")
    name = name.replace("\\", "")
    name = name.replace(":", "-")
    name = name.replace("*", "-")
    name = name.replace("?", "")
    name = name.replace('"', "")
    name = name.replace("<", "")
    name = name.replace(">", "")
    name = name.replace("|", "-")
    return name

def get_logo_url(name):
    """
    Prüft .PNG und .png Varianten und gibt die funktionierende Raw-URL zurück.
    """
    for ext in [".PNG", ".png"]:
        url = BASE_URL + name + ext
        try:
            r = requests.head(url)
            if r.status_code == 200:
                return url
        except requests.RequestException:
            continue
    return ""  # kein Logo gefunden

# --- M3U laden ---
response = requests.get(M3U_URL)
response.raise_for_status()
lines = response.text.splitlines()

# --- M3U verarbeiten ---
output_lines = []

for line in lines:
    if line.startswith("#EXTINF"):
        parts = line.split(",", 1)
        channel_name = parts[1].strip()
        safe_name = sanitize_filename(channel_name)
        logo_url = get_logo_url(safe_name)

        if 'tvg-logo="' in parts[0]:
            parts[0] = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', parts[0])
        else:
            parts[0] += f' tvg-logo="{logo_url}"'

        line = parts[0] + "," + channel_name

    output_lines.append(line)

# --- Output schreiben ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Fertig! '{OUTPUT_FILE}' erzeugt.")
