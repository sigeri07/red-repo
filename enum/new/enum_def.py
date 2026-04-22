import requests
import re
import urllib3
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

paths = [
    "/image",
    "/images",
    "/uploads",
    "/upload",
    "/i.php",
    "/info.php",
    "/phpinfo.php",
    "/s.php",
    "/upload.php",
    "/phpmyadmin"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

BASE_DIR = "pages"
os.makedirs(BASE_DIR, exist_ok=True)


def get_title(text):
    match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if match:
        return match.group(1).strip()
    return ""


def save_page(domain, path, content):

    # buat folder per subdomain
    domain_dir = os.path.join(BASE_DIR, domain)
    os.makedirs(domain_dir, exist_ok=True)

    # ubah path jadi nama file
    clean_path = path.strip("/").replace("/", "_")

    if clean_path == "":
        clean_path = "index"

    filename = f"{clean_path}.html"

    filepath = os.path.join(domain_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    return filepath


def scan(url, domain, proto, path):

    try:
        r = requests.get(
            url,
            timeout=5,
            verify=False,
            headers=headers
        )

        if r.status_code != 200:
            return

        title = get_title(r.text)

        saved_file = save_page(domain, path, r.content)

        if title:
            print(f"[200] {url} | {title} | saved: {saved_file}")
        else:
            print(f"[200] {url} | saved: {saved_file}")

        with lock:
            writer.writerow([
                domain,
                proto.replace("://",""),
                path,
                r.status_code,
                title,
                saved_file
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
    writer.writerow(["domain", "protocol", "path", "status", "title", "saved_file"])

    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(worker, domains)
