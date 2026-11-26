#!/usr/bin/env python3
"""
PathToFluent Scout

List films and series on Netflix that were made in Spain with Spanish as the
original language, using the free TMDB API (availability data from JustWatch).

Setup (once): create a free account at themoviedb.org, then Settings > API to
get a key. Either set it in your shell:   export TMDB_API_KEY=your_key
or pass it each time with --key.

Run:   python3 scout.py                  (US Netflix catalogue)
       python3 scout.py --region DE      (another country's catalogue)
       python3 scout.py --country MX     (made in Mexico instead)

Writes netflix_ES_es_US.csv next to where you run it and prints the top titles.
"""
import argparse, csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.themoviedb.org/3"
NETFLIX = 8      # TMDB's provider id for Netflix


def get(path, params, key):
    headers = {"Accept": "application/json"}
    if len(key) > 40:                       # long token = v4 "read access token"
        headers["Authorization"] = "Bearer " + key
    else:                                   # short key = v3 API key
        params = dict(params, api_key=key)
    url = "%s%s?%s" % (API, path, urllib.parse.urlencode(params))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit("TMDB rejected the key. Check it under Settings > API on themoviedb.org.")
            if e.code == 429 and attempt < 3:          # rate limited, wait and retry
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2)


def discover(kind, args, key):
    rows, page, pages = [], 1, 1
    while page <= min(pages, 500):
        data = get("/discover/" + kind, {
            "with_origin_country": args.country, "with_original_language": args.language,
            "with_watch_providers": NETFLIX, "watch_region": args.region,
            "sort_by": "popularity.desc", "include_adult": "false", "page": page}, key)
        pages = data.get("total_pages", 1)
        for r in data.get("results", []):
            origin = r.get("origin_country")
            if origin and args.country not in origin:   # belt and braces for series
                continue
            date = r.get("first_air_date") or r.get("release_date") or ""
            rows.append({
                "type": "Series" if kind == "tv" else "Film",
                "title": r.get("name") or r.get("title") or "",
                "original_title": r.get("original_name") or r.get("original_title") or "",
                "year": date[:4],
                "rating": r.get("vote_average") or 0,
                "votes": r.get("vote_count") or 0,
                "popularity": r.get("popularity") or 0,
                "link": "https://www.themoviedb.org/%s/%s" % (kind, r.get("id")),
            })
        page += 1
    return rows


def main():
    ap = argparse.ArgumentParser(description="Spain-made, Spanish-language titles on Netflix")
    ap.add_argument("--key", default=os.environ.get("TMDB_API_KEY", ""), help="TMDB API key or read access token")
    ap.add_argument("--region", default="US", help="Netflix catalogue country, two letters (default US)")
    ap.add_argument("--country", default="ES", help="country of origin, two letters (default ES = Spain)")
    ap.add_argument("--language", default="es", help="original language, two letters (default es)")
    ap.add_argument("--only", choices=["tv", "movie"], help="series only or films only")
    ap.add_argument("--min-votes", type=int, default=0, help="hide titles with fewer TMDB votes than this")
    args = ap.parse_args()
    args.region, args.country = args.region.upper(), args.country.upper()
    if not args.key:
        sys.exit("No TMDB key. Set TMDB_API_KEY or pass --key (free at themoviedb.org > Settings > API).")

    rows = []
    for kind in ([args.only] if args.only else ["tv", "movie"]):
        rows += discover(kind, args, args.key)
    rows = [r for r in rows if r["votes"] >= args.min_votes]
    rows.sort(key=lambda r: -r["popularity"])

    out = "netflix_%s_%s_%s.csv" % (args.country, args.language, args.region)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["type", "title", "original_title", "year", "rating", "votes", "link"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    series = sum(1 for r in rows if r["type"] == "Series")
    print("%d titles (%d series, %d films) on Netflix %s. Saved to %s\n" % (len(rows), series, len(rows) - series,
                                                                         args.region, out))
    for r in rows[:40]:
        print("  %-6s %-45s %s  %.1f" % (r["type"], r["title"][:45], r["year"] or "----", r["rating"]))
    if len(rows) > 40:
        print("  ... and %d more in the CSV" % (len(rows) - 40))
    print("\nData: TMDB. Streaming availability: JustWatch.")


if __name__ == "__main__":
    main()
