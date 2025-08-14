#!/usr/bin/env python3
import argparse, json, pathlib, re, time
from typing import List, Dict
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
UA = {"User-Agent": "speak-check/1.0 (education)"}

FOOTNOTE_RE = re.compile(r"\[.*?\]")


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    return r.text


def clean_country(name: str) -> str:
    name = FOOTNOTE_RE.sub("", str(name)).strip()
    name = name.replace("\xa0", " ")
    return name


def to_int(val) -> int:
    try:
        s = str(val).replace(",", "").strip()
        return int(float(s))
    except Exception:
        return None


def parse_population(html: str) -> List[Dict]:
    # First try pandas tables
    tables = pd.read_html(html)
    cand = None
    for t in tables:
        cols = {c.lower().strip() for c in t.columns}
        if ("country/area" in cols or "country or area" in cols or "country" in cols) and any(
            k in cols for k in ["population","population(1 july)","population(1 july 2023)"]
        ):
            cand = t
            break
    if cand is None:
        # Fallback: bs4
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.wikitable")
        rows = []
        if not table:
            return rows
        headers = [th.get_text(strip=True) for th in table.select("tr th")]
        for tr in table.select("tr")[1:]:
            tds = [td.get_text(strip=True) for td in tr.select("td")]
            if len(tds) >= 2:
                rows.append({"country": clean_country(tds[0]), "population": to_int(tds[1])})
        return rows

    df = cand.rename(columns=lambda c: str(c).strip())
    # Heuristic column names
    ctry_col = next((c for c in df.columns if c.lower().startswith("country")), None)
    pop_col = next((c for c in df.columns if "population" in c.lower()), None)
    year = None
    m = re.search(r"(\d{4})", pop_col or "")
    if m:
        year = int(m.group(1))
    df = df[[ctry_col, pop_col]].copy()
    df[ctry_col] = df[ctry_col].map(clean_country)
    df[pop_col] = df[pop_col].map(to_int)
    df = df.dropna()
    ts = int(time.time())
    out = []
    for _, r in df.iterrows():
        out.append({
            "country": r[ctry_col],
            "population": int(r[pop_col]),
            "year": year,
            "source_url": URL,
            "scraped_at": ts,
        })
    return out


def main(out: str):
    html = fetch_html(URL)
    recs = parse_population(html)
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() == ".csv":
        pd.DataFrame(recs).to_csv(p, index=False)
    else:
        p.write_text(json.dumps(recs, ensure_ascii=False, indent=2))
    print(f"Saved {len(recs)} records to {p}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/scraped/population.json")
    args = ap.parse_args()
    main(args.out)
