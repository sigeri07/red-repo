import requests
import urllib3
import hashlib
import csv
import os
import argparse
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

parser = argparse.ArgumentParser(description="Exposure Scanner with optional SOCKS proxy")
parser.add_argument("-p", "--proxy", help="SOCKS proxy (ex: socks5://127.0.0.1:9050)", default=None)
parser.add_argument("-t", "--threads", help="Number of threads", type=int, default=60)

args = parser.parse_args()

PROXY = args.proxy
THREADS = args.threads

paths = [
"/.git/HEAD",
"/.svn/entries",
"/web.config",
"/composer.json",
"/composer.lock",
"/package.json",
"/package-lock.json",
"/livewire/livewire.js",
"/vendor/composer/installed.json",
"/admin/environment.xml",
"/error_log",
"/storage/logs/laravel_log",
"/storage/logs/laravel.log",
"/.env",
"/app.zip",
"/website.zip",
"/wp-config.php.save",
"/wp-content/debug.log"
]

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def body_hash(data):
    return hashlib.md5(data).hexdigest()


def save_file(domain, path, content):

    filename = os.path.basename(path)

    if filename == "":
        filename = "index"

    safe_domain = domain.replace(":", "_")

    final_name = f"{safe_domain}_{filename}"

    filepath = os.path.join(DOWNLOAD_DIR, final_name)

    with open(filepath, "wb") as f:
        f.write(content)

    return filepath


def create_session():

    session = requests.Session()

    if PROXY:
        session.proxies.update({
            "http": PROXY,
            "https": PROXY
        })

    return session


def scan(domain):

    session = create_session()

    for proto in ["http://", "https://"]:

        base = proto + domain

        try:

            index = session.get(
                base,
                timeout=8,
                verify=False,
                headers=headers
            )

            index_hash = body_hash(index.content)
            index_len = len(index.content)

        except:
            continue

        for path in paths:

            url = base + path

            try:

                r = session.get(
                    url,
                    timeout=8,
                    verify=False,
                    headers=headers,
                    allow_redirects=True
                )

                if r.status_code != 200:
                    continue

                content_type = r.headers.get("Content-Type", "").lower()

                if "text/html" in content_type:
                    continue

                size = len(r.content)

                if size < 50:
                    continue

                h = body_hash(r.content)

                if h == index_hash:
                    continue

                if abs(size - index_len) < 50:
                    continue

                file_path = save_file(domain, path, r.content)

                print(f"[{r.status_code}] {url} | {content_type} | {size} | saved: {file_path}")

                with lock:
                    writer.writerow([
                        domain,
                        proto.replace("://",""),
                        path,
                        r.status_code,
                        content_type,
                        size,
                        file_path
                    ])

            except:
                pass


with open("w.txt") as f:
    domains = [x.strip() for x in f if x.strip()]


with open("exposures.csv", "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)
    writer.writerow(["domain","protocol","path","status","content_type","size","saved_file"])

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(scan, domains)
