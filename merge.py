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
channel_groups = defaultdict(list)
movie_entries = []
radio_entries = []

# ভিওডি / মুভি ফিল্টার কিওয়ার্ড
vod_keywords = [
    "vod", "series", "episode", "season", "1080p", "720p", "4k",
    "bluray", "web-dl", "webrip", "hdrip", "dvdrip", "x264", "hevc", "full movie"
]
movie_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']

# রেডিও ফিল্টার কিওয়ার্ড
radio_keywords = ["radio", " fm", "fm ", "-fm", "fm-", "audio", "betar", "বাংলাদেশ বেতার"]
radio_extensions = ['.mp3', '.aac', '.ogg', '.pls']

def extract_channel_name(extinf):
    """#EXTINF লাইন থেকে চ্যানেলের মূল নাম বের করার ফাংশন"""
    if ',' in extinf:
        name = extinf.split(',')[-1].strip()
        # ক্লিন করার জন্য HD, SD, BDIX ইত্যাদি বাদ দিয়ে মূল নাম নেওয়া
        name_clean = re.sub(r'\s*\b(hd|sd|fhd|4k|720p|1080p|bdix|server\s*\d+|src\s*\d+)\b', '', name, flags=re.IGNORECASE)
        return name_clean.strip() if name_clean.strip() else name
    return "Others"

def update_group_title(extinf, group_name):
    """#EXTINF লাইনে নির্দিষ্ট চ্যানেলের নামে group-title আপডেট/যোগ করার ফাংশন"""
    if 'group-title="' in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{group_name}"', extinf)
    else:
        # group-title ট্যাগ না থাকলে বসিয়ে দেওয়া
        return re.sub(r'(#EXTINF:[^\s,]+)', r'\1 group-title="' + group_name + '"', extinf)

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

            # ১. শুধুমাত্র স্ট্রিমিং ইউআরএল ফিল্টার করা (ডুপ্লিকেট ঢুকবে না)
            if stream_url not in seen_urls:
                seen_urls.add(stream_url)
                
                combined_text = (extinf_line + " " + stream_url).lower()

                # ক. রেডিও
                is_radio_ext = any(ext in stream_url.lower() for ext in radio_extensions)
                is_radio_kw = any(kw in combined_text for kw in radio_keywords)

                # খ. মুভি ও ভিওডি
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
                    # গ. লাইভ টিভি চ্যানেল গ্রুপিং
                    ch_name = extract_channel_name(extinf_line)
                    # group-title ট্যাগে চ্যানেলের মূল নাম সেট করা
                    updated_extinf = update_group_title(extinf_line, ch_name)
                    channel_groups[ch_name.lower()].append((updated_extinf, stream_url))

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
                channel_groups["others"].append(('#EXTINF:-1 group-title="Others", Unknown Channel', stream_url))
    i += 1

# সকল চ্যানেল গ্রুপ অনুযায়ী সর্ট করে একটি একক লিস্ট তৈরি করা
sorted_channel_entries = []
for ch_key in sorted(channel_groups.keys()):
    sorted_channel_entries.extend(channel_groups[ch_key])

bd_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=6)))
updated_time_str = bd_time.strftime("%Y-%m-%d %H:%M:%S (BD Time)")

epg_url = "https://epgshare01.online/epgshare01/epg_ripper_AL1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"

# ১. টিভি প্লেলিস্ট রাইট করা
with open("BDIX-Playlist.m3u", "w", encoding="utf-8") as f:
    f.write(f'#EXTM3U x-tvg-url="{epg_url}"\n\n')
    f.write("#=================================\n")
    f.write("# 🖥️ Developed by: Ahammad Ali\n")
    f.write("# 🔗 Telegram: https://t.me/banglatvlivefree\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 📺 Channels Count: {len(sorted_channel_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in sorted_channel_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

# ২. মুভি প্লেলিস্ট রাইট করা
with open("BDIX-Movies.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    f.write("#=================================\n")
    f.write("# 🎬 Movies & On-Demand Playlist\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 🍿 Movies Count: {len(movie_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in movie_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

# ৩. রেডিও প্লেলিস্ট রাইট করা
with open("BDIX-Radio.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    f.write("#=================================\n")
    f.write("# 📻 Live Radio Playlist\n")
    f.write(f"# 🕒 Last Updated: {updated_time_str}\n")
    f.write(f"# 📻 Radio Count: {len(radio_entries)}\n")
    f.write("#=================================\n\n")
    
    for extinf, stream_url in radio_entries:
        if extinf:
            f.write(extinf + "\n")
        f.write(stream_url + "\n")

print("Channel grouping complete!")
