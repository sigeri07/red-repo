import requests
import urllib3
import hashlib
import csv
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

paths = [
"/.git/HEAD",
"/.svn/entries",
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

# folder download
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


def scan(domain):

    session = requests.Session()

    for proto in ["http://", "https://"]:

        base = proto + domain

        try:

            index = session.get(
                base,
                timeout=5,
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
                    timeout=5,
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

    with ThreadPoolExecutor(max_workers=60) as executor:
        executor.map(scan, domains)
