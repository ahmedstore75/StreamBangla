import urllib.request
import datetime
import re

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
channel_entries = []
movie_entries = []
radio_entries = []

# ১. ভিওডি / মুভি ফিল্টার কিওয়ার্ড
vod_keywords = [
    "vod", "series", "episode", "season", "1080p", "720p", "4k",
    "bluray", "web-dl", "webrip", "hdrip", "dvdrip", "x264", "hevc", "full movie"
]
movie_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']

# ২. রেডিও ফিল্টার কিওয়ার্ড
radio_keywords = ["radio", " fm", "fm ", "-fm", "fm-", "audio", "betar", "বাংলাদেশ বেতার"]
radio_extensions = ['.mp3', '.aac', '.ogg', '.pls']

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

            # হুবহু পুরো স্ট্রিম ইউআরএল একবার ফিল্টার করার চেক
            if stream_url not in seen_urls:
                seen_urls.add(stream_url)
                
                combined_text = (extinf_line + " " + stream_url).lower()

                # ক. রেডিও চেকিং
                is_radio_ext = any(ext in stream_url.lower() for ext in radio_extensions)
                is_radio_kw = any(kw in combined_text for kw in radio_keywords)

                # খ. মুভি ও ভিওডি চেকিং
                is_movie_ext = any(stream_url.lower().endswith(ext) or (ext + "?") in stream_url.lower() for ext in movie_extensions)
                is_vod_kw = any(kw in combined_text for kw in vod_keywords)

                duration_match = re.search(r"#EXTINF:([0-9]+)", extinf_line)
                is_fixed_duration = False
                if duration_match:
                    duration = int(duration_match.group(1))
                    if duration > 1800:
                        is_fixed_duration = True

                # ক্যাটাগরি অনুযায়ী ফিল্টার করা
                if is_radio_ext or is_radio_kw:
                    radio_entries.append((extinf_line, stream_url))
                elif is_movie_ext or is_vod_kw or is_fixed_duration:
                    movie_entries.append((extinf_line, stream_url))
                else:
                    channel_entries.append((extinf_line, stream_url))

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
                channel_entries.append(("", stream_url))
    i += 1

bd_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=6)))
updated_time_str = bd_time.strftime("%Y-%m-%d %H:%M:%S (BD Time)")

epg_url = "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ALJAZEERA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_AR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ASIANTELEVISION1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_AT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BE2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BEIN1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BG1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CO1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CY1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_CZ1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DELUXEMUSIC1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DIRECTVSPORTS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DISTROTV1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DO1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DRAFTKINGS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_EC1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_EG1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_FI1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_FR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_GR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_HK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_HU1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ID1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_IE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_IL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_JM1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_JP1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_JP2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_KE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_KR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_LT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_LV1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_MT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_MX1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_NG1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_NO1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PAC-12.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PLEX1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_POWERNATION1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_DE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_EN1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_ES1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_FR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_IT1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_NL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN_PL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RALLY_TV1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RO1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RO2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_RS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SA2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SE1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SPORTKLUB1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SSPORTPLUS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_SV1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_TBNPLUS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_THESPORTPLUS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_TR3.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_UY1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_VN1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_VOA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ZA1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_viva-russia.ru.xml.gz"

# ১. টিভি প্লেলিস্ট
with open("BDIX-Playlist.m3u", "w", encoding="utf-8") as f:
    f.write(f'#EXTM3U x-tvg-url="{epg_url}"\n\n')
    f.write("#=================================\n")
    f.write("# 🖥️ Developed by: Ahammad Ali\n")
    f.write("# 🔗 Telegram: https://t.me/banglatvlivefree\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 📺 Channels Count: {len(channel_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in channel_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

# ২. মুভি প্লেলিস্ট
with open("BDIX-Movies.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    f.write("#=================================\n")
    f.write("# 🎬 Movies & On-Demand Playlist\n")
    f.write("# 🖥️ Developed by: Ahammad Ali\n")
    f.write("# 🔗 Telegram: https://t.me/banglatvlivefree\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 🍿 Movies Count: {len(movie_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in movie_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

# ৩. রেডিও প্লেলিস্ট
with open("BDIX-Radio.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    f.write("#=================================\n")
    f.write("# 📻 Live Radio Playlist\n")
    f.write("# 🖥️ Developed by: Ahammad Ali\n")
    f.write("# 🔗 Telegram: https://t.me/banglatvlivefree\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 📻 Radio Count: {len(radio_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in radio_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

print(f"Complete! Unique Channels: {len(channel_entries)}, Movies: {len(movie_entries)}, Radios: {len(radio_entries)}")
