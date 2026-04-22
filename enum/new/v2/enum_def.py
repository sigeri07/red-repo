import requests
import re
import urllib3
import csv
import argparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

paths = [
    "/image",
    "/dashboard",
    "/images",
    "/uploads",
    "/upload",
    "/i.php",
    "/info.php",
    "/phpinfo.php",
    "/s.php",
    "/phpmyadmin",
    "/upload.php"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--proxy", help="SOCKS proxy example: socks5://127.0.0.1:9050")
args = parser.parse_args()

proxies = None
if args.proxy:
    proxies = {
        "http": args.proxy,
        "https": args.proxy
    }


def get_title(text):
    match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if match:
        return match.group(1).strip()
    return ""


def scan(url, domain, proto, path):

    try:

        r = requests.get(
            url,
            timeout=5,
            verify=False,
            headers=headers,
            proxies=proxies
        )

        if r.status_code != 200:
            return

        title = get_title(r.text)

        if title:
            print(f"[200] {url} | {title}")
        else:
            print(f"[200] {url}")

        with lock:
            writer.writerow([
                domain,
                proto.replace("://",""),
                path,
                r.status_code,
                title
            ])

    except:
        pass


def worker(domain):

    for proto in ["http://", "https://"]:

        base = proto + domain

        for path in paths:

            url = base + path

            scan(url, domain, proto, path)


with open("w.txt") as f:
    domains = [x.strip() for x in f if x.strip()]


with open("enum_def.csv", "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)
    writer.writerow(["domain", "protocol", "path", "status", "title"])

    print(f"[INFO] Domains loaded: {len(domains)}")

    if proxies:
        print(f"[INFO] Using proxy: {args.proxy}")

    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(worker, domains)
