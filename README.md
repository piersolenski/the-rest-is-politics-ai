# The Rest Is Politics: AI Series

The AI-focused episodes from *The Rest Is Politics*, served as a podcast feed.

## Subscribe

Paste this URL into your podcast app ("Add Show by URL" in Apple Podcasts, Overcast, Pocket Casts, etc.):

```
https://piersolenski.github.io/the-rest-is-politics-ai/feed.xml
```

## Episodes (chronological listening order)

1. How Will AI Change The World? - 2025-12-12
2. Will AI Take Our Jobs? - 2025-12-19
3. China Vs USA: Who Will Win the AI Race? - 2026-01-09
4. Will AI End Humanity? - 2026-01-16
5. What If the AI Revolution Isn't Real? - 2026-01-26
6. The Future of Warfare: Anthropic vs OpenAI - 2026-03-06
7. Who Is Really Running the AI Revolution? - 2026-03-27
8. LEADING: Will AI Give China or the US Total Power? (William MacAskill) - 2026-05-10
9. LEADING: Is It Already Too Late to Control AI? (Anthropic Co-Founder, Jack Clark) - 2026-05-31

## How it works

- `feed.xml` is a static RSS 2.0 + iTunes-namespace podcast feed, served by GitHub Pages.
- The MP3 files are uploaded as assets on the `v1` GitHub Release, served by GitHub's CDN.
- `generate_feed.py` regenerates `feed.xml` from a cached copy of the source RSS feed.

## Regenerating after adding episodes

1. Drop the new MP3 into `episodes/` following the `NN-slug.mp3` naming.
2. Add an entry to `EPISODE_MAP` in `generate_feed.py`.
3. `python3 generate_feed.py`
4. `gh release upload v1 episodes/NN-slug.mp3`
5. `git add feed.xml README.md && git commit -m "feed: add episode NN" && git push`

## Credits

Original podcast (c) Goalhanger Podcasts. This repo exists only for personal convenience and is not affiliated with or endorsed by The Rest Is Politics.
