#!/usr/bin/env python3
"""Generate feed.xml for the curated AI episodes.

Reads:
  - /tmp/feed.xml (source feed cache - title/description/duration/pubDate)
  - episodes/*.mp3 (local audio files - filename -> source item match, byte length)

Writes:
  - feed.xml in the script's directory
"""
import os
import re
import sys
from datetime import timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
EPS_DIR = ROOT / "episodes"
SOURCE = Path("/tmp/feed.xml")
OUT = ROOT / "feed.xml"

REPO_OWNER = "piersolenski"
REPO_NAME = "the-rest-is-politics-ai"
RELEASE_TAG = "v1"
ASSET_BASE = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{RELEASE_TAG}"
PAGES_BASE = f"https://{REPO_OWNER}.github.io/{REPO_NAME}"
ARTWORK = ("https://megaphone.imgix.net/podcasts/210911d2-01fc-11ed-ae3f-fff33860d23a/"
           "image/5aaf8b0916f97b04cc05ff654c4fcff1.jpg")

CHANNEL = {
    "title": "The Rest Is Politics: AI Series (Personal Mix)",
    "description": (
        "A curated playlist of the AI-focused episodes from The Rest Is Politics, "
        "covering the December 2025 - May 2026 arc with Rory Stewart and Matt Clifford, "
        "plus two Leading interviews (William MacAskill, Jack Clark of Anthropic). "
        "Audio rehosted for personal listening. Original podcast (c) Goalhanger Podcasts."
    ),
    "author": "Goalhanger Podcasts (curated by Piers)",
    "owner_name": "Piers Olenski",
    "owner_email": "hello@piers.io",
    "language": "en",
    "explicit": "no",
}

EPISODE_MAP = [
    ("01-how-will-ai-change-the-world.mp3",
        "How Will AI Change The World? (Ep 1) | FULL EPISODE"),
    ("02-will-ai-take-our-jobs.mp3",
        "Will AI Take Our Jobs? (Ep 2) | FULL EPISODE"),
    ("03-china-vs-usa-who-will-win-the-ai-race.mp3",
        "China Vs USA: Who Will Win the AI Race? (Ep 3) | FULL EPISODE"),
    ("04-will-ai-end-humanity.mp3",
        "Will AI End Humanity? | FULL EPISODE"),
    ("05-what-if-the-ai-revolution-isnt-real.mp3",
        "What If the AI Revolution"),
    ("06-the-future-of-warfare-anthropic-vs-openai.mp3",
        "The Future of Warfare: Anthropic vs OpenAI"),
    ("07-who-is-really-running-the-ai-revolution.mp3",
        "Who Is Really Running the AI Revolution?"),
    ("08-leading-will-ai-give-china-or-us-total-power-macaskill.mp3",
        "Will AI Give China or the US Total Power"),
    ("09-leading-is-it-already-too-late-to-control-ai-jack-clark.mp3",
        "Is It Already Too Late to Control AI"),
]


def parse_source_items():
    data = SOURCE.read_text(encoding="utf-8")
    raw_items = re.findall(r"<item>.*?</item>", data, re.DOTALL)
    items = []
    for raw in raw_items:
        title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", raw, re.DOTALL)
        desc_m = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", raw, re.DOTALL)
        sum_m = re.search(r"<itunes:summary>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</itunes:summary>", raw, re.DOTALL)
        pub_m = re.search(r"<pubDate>([^<]+)</pubDate>", raw)
        dur_m = re.search(r"<itunes:duration>([^<]+)</itunes:duration>", raw)
        guid_m = re.search(r"<guid[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</guid>", raw, re.DOTALL)
        if not (title_m and pub_m):
            continue
        items.append({
            "title": title_m.group(1).strip(),
            "description": (desc_m.group(1).strip() if desc_m else ""),
            "summary": (sum_m.group(1).strip() if sum_m else ""),
            "pubdate_raw": pub_m.group(1).strip(),
            "duration": dur_m.group(1).strip() if dur_m else "",
            "guid": guid_m.group(1).strip() if guid_m else "",
        })
    return items


def find_by_needle(items, needle):
    for it in items:
        if needle in it["title"]:
            return it
    raise SystemExit(f"No source item matches: {needle!r}")


def fmt_duration(d):
    if not d: return ""
    if ":" in d: return d
    try:
        s = int(d)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{sec:02d}"
    except ValueError:
        return d


def build_item(src, filename, ep_num):
    path = EPS_DIR / filename
    if not path.exists():
        raise SystemExit(f"Missing audio file: {path}")
    size = path.stat().st_size
    pubdate_dt = parsedate_to_datetime(src["pubdate_raw"])
    if pubdate_dt.tzinfo is None:
        pubdate_dt = pubdate_dt.replace(tzinfo=timezone.utc)
    pubdate_822 = format_datetime(pubdate_dt)
    asset_url = f"{ASSET_BASE}/{filename}"
    title = escape(src["title"])
    desc = src["description"]
    summary = src["summary"] or desc
    # GUID: deterministic but distinct from source feed so apps don't mark as played
    guid = f"piers-trip-ai-{ep_num:02d}-{filename}"

    return f"""    <item>
      <title>{title}</title>
      <description><![CDATA[{desc}]]></description>
      <itunes:summary><![CDATA[{summary}]]></itunes:summary>
      <itunes:author>{escape(CHANNEL['author'])}</itunes:author>
      <pubDate>{pubdate_822}</pubDate>
      <enclosure url="{asset_url}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(guid)}</guid>
      <itunes:duration>{fmt_duration(src['duration'])}</itunes:duration>
      <itunes:episode>{ep_num}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>no</itunes:explicit>
      <itunes:image href="{ARTWORK}"/>
    </item>"""


def main():
    items = parse_source_items()
    print(f"Parsed {len(items)} source items", file=sys.stderr)

    rendered = []
    for idx, (filename, needle) in enumerate(EPISODE_MAP, start=1):
        src = find_by_needle(items, needle)
        rendered.append((src["pubdate_raw"], build_item(src, filename, idx)))
        print(f"  + {idx:02d} {src['title']}", file=sys.stderr)

    # Newest-first ordering by pubDate (RSS convention)
    rendered.sort(
        key=lambda r: parsedate_to_datetime(r[0]).replace(tzinfo=timezone.utc)
        if parsedate_to_datetime(r[0]).tzinfo is None
        else parsedate_to_datetime(r[0]),
        reverse=True,
    )
    items_xml = "\n".join(r[1] for r in rendered)

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     version="2.0">
  <channel>
    <title>{escape(CHANNEL['title'])}</title>
    <link>{PAGES_BASE}/</link>
    <atom:link href="{PAGES_BASE}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>{CHANNEL['language']}</language>
    <description><![CDATA[{CHANNEL['description']}]]></description>
    <itunes:author>{escape(CHANNEL['author'])}</itunes:author>
    <itunes:summary><![CDATA[{CHANNEL['description']}]]></itunes:summary>
    <itunes:explicit>{CHANNEL['explicit']}</itunes:explicit>
    <itunes:type>episodic</itunes:type>
    <itunes:owner>
      <itunes:name>{escape(CHANNEL['owner_name'])}</itunes:name>
      <itunes:email>{escape(CHANNEL['owner_email'])}</itunes:email>
    </itunes:owner>
    <itunes:image href="{ARTWORK}"/>
    <itunes:category text="News">
      <itunes:category text="Politics"/>
    </itunes:category>
    <image>
      <url>{ARTWORK}</url>
      <title>{escape(CHANNEL['title'])}</title>
      <link>{PAGES_BASE}/</link>
    </image>
{items_xml}
  </channel>
</rss>
"""
    OUT.write_text(feed, encoding="utf-8")
    print(f"\nWrote {OUT} ({len(feed):,} chars)", file=sys.stderr)


if __name__ == "__main__":
    main()
