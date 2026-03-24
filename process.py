import re
import requests
import urllib.parse

# --- Einstellungen ---
BASE_URL = "https://raw.githubusercontent.com/calvinklein97/German-Free-IPTV/refs/heads/main/Logos/"
M3U_URL = "https://iptv-org.github.io/iptv/languages/deu.m3u"
OUTPUT_FILE = "output.m3u"

# --- Mapping für M3U-Namen (ohne Umlaute) → echte Dateinamen im Repo ---
name_mapping = {
    "Allgau TV (1080p)": "Allgäu TV (1080p)",
    "Osterreich TV (1080p)": "Österreich TV (1080p)",
    # hier alle weiteren Kanäle ergänzen, die Umlaut-/ASCII-Abweichungen haben
    # Beispiel: "Augsburg TV (1080p)": "Augsburg TV (1080p)"
}

# --- Hilfsfunktionen ---
def sanitize_for_url(name):
    """
    Entfernt problematische Zeichen (/, \, |) und URL-encodiert
    """
    name = name.replace("/", "")
    name = name.replace("\\", "")
    name = name.replace("|", "-")
    return urllib.parse.quote(name)

def get_repo_name(m3u_name):
    """
    Mappt M3U-Namen auf echten Dateinamen
    """
    return name_mapping.get(m3u_name, m3u_name)

def get_logo_url(name):
    """
    Prüft .PNG und .png Varianten und gibt die funktionierende Raw-URL zurück.
    """
    safe_name = sanitize_for_url(name)
    for ext in [".PNG", ".png"]:
        url = f"{BASE_URL}{safe_name}{ext}"
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
        repo_name = get_repo_name(channel_name)
        logo_url = get_logo_url(repo_name)

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
