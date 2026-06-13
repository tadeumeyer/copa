#!/usr/bin/env python3
import os
import sys
import requests

FIGMA_TOKEN = os.environ["FIGMA_TOKEN"]
FILE_KEY = "eVEXECqP4Zmmz88uxhn836"
CACHE_FILE = ".figma-cache/last-modified.txt"

FRAMES = {
    "787:3979": "canal/canal-copa-grupoA",
    "787:4150": "canal/canal-copa-grupoB",
    "787:4321": "canal/canal-copa-grupoC",
    "787:4492": "canal/canal-copa-grupoD",
    "787:4834": "canal/canal-copa-grupoE",
    "787:5176": "canal/canal-copa-grupoF",
    "787:5518": "canal/canal-copa-grupoG",
    "787:5860": "canal/canal-copa-grupoH",
    "787:6202": "canal/canal-copa-grupoI",
    "787:6544": "canal/canal-copa-grupoJ",
    "787:6886": "canal/canal-copa-grupoK",
    "787:7228": "canal/canal-copa-grupoL",
    "906:1392": "redes/redes-copa-grupoA",
    "915:4961": "redes/redes-copa-grupoB",
    "915:5181": "redes/redes-copa-grupoC",
    "915:5401": "redes/redes-copa-grupoD",
    "915:5621": "redes/redes-copa-grupoE",
    "915:5841": "redes/redes-copa-grupoF",
    "915:6061": "redes/redes-copa-grupoG",
    "915:6281": "redes/redes-copa-grupoH",
    "915:6501": "redes/redes-copa-grupoI",
    "915:6721": "redes/redes-copa-grupoJ",
    "915:6941": "redes/redes-copa-grupoK",
    "915:7161": "redes/redes-copa-grupoL",
}

HEADERS = {"X-Figma-Token": FIGMA_TOKEN}


def get_last_modified():
    r = requests.get(
        f"https://api.figma.com/v1/files/{FILE_KEY}?depth=1",
        headers=HEADERS, timeout=30,
    )
    r.raise_for_status()
    return r.json()["lastModified"]


def get_export_urls(node_ids):
    all_images = {}
    batch_size = 5
    for i in range(0, len(node_ids), batch_size):
        batch = node_ids[i : i + batch_size]
        ids_str = ",".join(batch)
        url = f"https://api.figma.com/v1/images/{FILE_KEY}?ids={ids_str}&scale=2&format=png"
        print(f"  Batch {i // batch_size + 1}: {ids_str}")
        r = requests.get(url, headers=HEADERS, timeout=60)
        if not r.ok:
            print(f"  Figma API error {r.status_code}: {r.text}")
            r.raise_for_status()
        data = r.json()
        if data.get("err"):
            raise RuntimeError(f"Figma export error: {data['err']}")
        all_images.update(data["images"])
    return all_images


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    last_modified = get_last_modified()
    print(f"Figma file last modified: {last_modified}")

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            if f.read().strip() == last_modified:
                print("No changes detected — skipping export.")
                sys.exit(0)

    print("Changes detected — exporting all 24 frames at 2x…")
    images = get_export_urls(list(FRAMES.keys()))

    for node_id, url in images.items():
        if not url:
            print(f"  WARNING: no URL for {node_id}")
            continue
        dest = f"exports/{FRAMES[node_id]}.png"
        print(f"  {node_id} → {dest}")
        download(url, dest)

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        f.write(last_modified)

    print("Export complete.")


if __name__ == "__main__":
    main()
