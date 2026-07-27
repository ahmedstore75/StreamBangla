import urllib.request
import datetime
import re
from collections import defaultdict

urls = [
    "https://raw.githubusercontent.com/ahmedstore75/Iptvbdlive/main/mixiptvchannel.m3u",
    "https://raw.githubusercontent.com/ahan443/FAST-IPTV/refs/heads/main/combined_playlist.m3u",
    "https://raw.githubusercontent.com/bugsfreeweb/LiveTVCollector/refs/heads/main/LiveTV/Bangladesh/LiveTV.m3u",
    "https://raw.githubusercontent.com/sm-monirulislam/SM-Live-TV/refs/heads/main/Combined_Live_TV.m3u"
]

raw_lines = []
for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
            raw_lines.extend([line.strip() for line in content.splitlines() if line.strip()])
    except Exception as e:
        print(f"Error fetching {url}: {e}")

seen_urls = set()
channel_map = defaultdict(list)
movie_entries = []
radio_entries = []

vod_keywords = [
    "vod", "series", "episode", "season", "1080p", "720p", "4k",
    "bluray", "web-dl", "webrip", "hdrip", "dvdrip", "x264", "hevc", "full movie"
]
movie_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']

radio_keywords = ["radio", " fm", "fm ", "-fm", "fm-", "audio", "betar", "বাংলাদেশ বেতার"]
radio_extensions = ['.mp3', '.aac', '.ogg', '.pls']

def get_clean_channel_name(extinf):
    """EXTINF থেকে চ্যানেলের মূল নাম ক্লিন করে বের করে নেওয়া"""
    if ',' in extinf:
        name = extinf.split(',')[-1].strip()
        # সার্ভার বা এইচডি শব্দ সরিয়ে মূল নাম বের করা
        name_clean = re.sub(r'\s*\b(hd|sd|fhd|4k|720p|1080p|bdix|server\s*\d+|src\s*\d+|bkp|backup)\b', '', name, flags=re.IGNORECASE)
        return name_clean.strip() if name_clean.strip() else name
    return "Unknown Channel"

i = 0
while i < len(raw_lines):
    line = raw_lines[i]
    if line.startswith("#EXTINF"):
        extinf_line = line
        i += 1
        while i < len(raw_lines) and raw_lines[i].startswith("#"):
            i += 1
        if i < len(raw_lines):
            stream_url = raw_lines[i]

            if stream_url not in seen_urls:
                seen_urls.add(stream_url)
                
                combined_text = (extinf_line + " " + stream_url).lower()

                is_radio_ext = any(ext in stream_url.lower() for ext in radio_extensions)
                is_radio_kw = any(kw in combined_text for kw in radio_keywords)

                is_movie_ext = any(stream_url.lower().endswith(ext) or (ext + "?") in stream_url.lower() for ext in movie_extensions)
                is_vod_kw = any(kw in combined_text for kw in vod_keywords)

                duration_match = re.search(r"#EXTINF:([0-9]+)", extinf_line)
                is_fixed_duration = False
                if duration_match:
                    duration = int(duration_match.group(1))
                    if duration > 1800:
                        is_fixed_duration = True

                if is_radio_ext or is_radio_kw:
                    radio_entries.append((extinf_line, stream_url))
                elif is_movie_ext or is_vod_kw or is_fixed_duration:
                    movie_entries.append((extinf_line, stream_url))
                else:
                    ch_name = get_clean_channel_name(extinf_line)
                    channel_map[ch_name.lower()].append((extinf_line, stream_url, ch_name))

    elif not line.startswith("#"):
        stream_url = line
        if stream_url not in seen_urls:
            seen_urls.add(stream_url)
            url_lower = stream_url.lower()

            is_radio = any(ext in url_lower for ext in radio_extensions) or any(kw in url_lower for kw in radio_keywords)
            is_movie = any(url_lower.endswith(ext) or (ext + "?") in url_lower for ext in movie_extensions) or any(kw in url_lower for kw in vod_keywords)

            if is_radio:
                radio_entries.append(("", stream_url))
            elif is_movie:
                movie_entries.append(("", stream_url))
            else:
                channel_map["others"].append(('EXTINF:-1 group-title="Others", Unknown Channel', stream_url, "Unknown Channel"))
    i += 1

bd_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=6)))
updated_time_str = bd_time.strftime("%Y-%m-%d %H:%M:%S (BD Time)")

epg_url = "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"

# টিভি প্লেলিস্ট সেভ
with open("BDIX-Playlist.m3u", "w", encoding="utf-8") as f:
    f.write(f'#EXTM3U x-tvg-url="{epg_url}"\n\n')
    f.write("#=================================\n")
    f.write("# 🖥️ Developed by: Ahammad Ali\n")
    f.write("# 🔗 Telegram: https://t.me/banglatvlivefree\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write("#=================================\n\n")
    
    for ch_key in sorted(channel_map.keys()):
        items = channel_map[ch_key]
        for index, (extinf, stream_url, clean_name) in enumerate(items, start=1):
            # প্লেয়ারের অটো-সুইচ সুবিধার জন্য সার্ভার ১, ২, ৩ আকারে সাজানো
            if len(items) > 1:
                display_name = f"{clean_name} (Server {index})"
            else:
                display_name = clean_name

            # EXTINF লাইনে সঠিক চ্যানেলের নাম পুনর্স্থাপন
            if ',' in extinf:
                base_extinf = extinf.rsplit(',', 1)[0]
                updated_extinf = f"{base_extinf},{display_name}"
            else:
                updated_extinf = f'#EXTINF:-1 group-title="Bangla",{display_name}'

            f.write(updated_extinf + "\n")
            f.write(stream_url + "\n")

# মুভি ও রেডিও প্লেলিস্ট
with open("BDIX-Movies.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for extinf, stream_url in movie_entries:
        if extinf: f.write(extinf + "\n")
        f.write(stream_url + "\n")

with open("BDIX-Radio.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for extinf, stream_url in radio_entries:
        if extinf: f.write(extinf + "\n")
        f.write(stream_url + "\n")

print("Auto-failover/backup arrangement complete!")
