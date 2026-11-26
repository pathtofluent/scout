# PathToFluent Scout

Lists the films and series on Netflix that were made in a given country in its own language, for example everything made in Spain in Spanish. Netflix's own search can't filter that way.

Status: early.

## Run it

```
python3 scout.py --key YOUR_TMDB_KEY                 # Spain, Spanish, US Netflix
python3 scout.py --region DE --country MX            # Mexico-made titles on German Netflix
python3 scout.py --only tv --min-votes 50            # series only, skip obscure titles
```

You need a free API key from themoviedb.org (Settings > API). Set it once with `export TMDB_API_KEY=your_key` to skip `--key`.

It prints the most popular titles and saves the full list as a CSV with title, year, rating and a link.

## Limits

- It finds "made in this country, originally in this language". It does not read Netflix's actual audio track list.
- Availability comes from JustWatch through TMDB and can lag by a few days.
- Netflix shows you the catalogue of the country you are in; set `--region` to match.

Data: TMDB. Streaming availability: JustWatch. This tool is not endorsed by either, or by Netflix.

## The PathToFluent tools

| Tool | What it does |
|------|--------------|
| [Trailblazer](https://github.com/pathtofluent/trailblazer) | Turns a video and its subtitles into an Anki deck |
| [Waypoint](https://github.com/pathtofluent/waypoint) | Sorts sentence cards so the next one has exactly one unknown word |
| [Checkpoint](https://github.com/pathtofluent/checkpoint) | A single Complete button for chapter and lesson cards |
| [Scout](https://github.com/pathtofluent/scout) | Finds Netflix titles by country and original language |

## Licence

GNU AGPL v3 or later. See `LICENSE`.
