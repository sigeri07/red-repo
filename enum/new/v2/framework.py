import requests
import re
import urllib3
import csv
import argparse
import time
import random
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()
proxy_lock = Lock()

parser = argparse.ArgumentParser()
parser.add_argument("--safe", action="store_true", help="Safe scanning mode")
parser.add_argument("--aggressive", action="store_true", help="Aggressive scanning mode")
parser.add_argument("-p", "--proxy", help="Single SOCKS proxy example: socks5://127.0.0.1:9050")
parser.add_argument("--proxy-list", help="File containing proxy list")
parser.add_argument("--retries", type=int, default=2, help="Retry attempts")
args = parser.parse_args()

threads = 30
delay = (0, 0)

if args.safe:
    threads = 10
    delay = (0.5, 2)

if args.aggressive:
    threads = 80
    delay = (0, 0)

proxy_list = []

if args.proxy_list:
    with open(args.proxy_list) as f:
        proxy_list = [x.strip() for x in f if x.strip()]

single_proxy = args.proxy


def get_proxy():

    if single_proxy:
        return {
            "http": single_proxy,
            "https": single_proxy
        }

    if proxy_list:
        with proxy_lock:
            p = random.choice(proxy_list)

        return {
            "http": p,
            "https": p
        }

    return None


def get_title(text):
    match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if match:
        return match.group(1).strip()
    return ""


def detect_framework(resp):

    body = resp.text.lower()
    headers_text = str(resp.headers).lower()
    cookies = str(resp.cookies).lower()

    if "wp-content" in body or "wordpress" in body:
        return "WordPress"

    if "laravel_session" in cookies:
        return "Laravel"

    if "csrfmiddlewaretoken" in body or "csrftoken" in cookies:
        return "Django"

    if "drupal-settings-json" in body:
        return "Drupal"

    if "joomla" in body:
        return "Joomla"

    if "asp.net" in headers_text or "asp.net_sessionid" in cookies:
        return "ASP.NET"

    if "x-powered-by" in headers_text:
        return resp.headers.get("X-Powered-By", "")

    return ""


def fetch(url):

    for _ in range(args.retries + 1):

        try:

            proxy = get_proxy()

            r = requests.get(
                url,
                timeout=6,
                verify=False,
                headers=headers,
                proxies=proxy,
                allow_redirects=True
            )

            return r

        except:
            time.sleep(0.5)

    return None


def scan(domain):

    found = False

    for proto in ["http://", "https://"]:

        url = proto + domain

        if delay != (0,0):
            time.sleep(random.uniform(*delay))

        r = fetch(url)

        if not r:
            continue

        title = get_title(r.text)
        framework = detect_framework(r)
        size = len(r.content)

        output = f"[{r.status_code}] {url} [{size}]"

        if title:
            output += f" | {title}"

        if framework:
            output += f" | {framework}"

        print(output)

        with lock:

            writer.writerow([
                domain,
                proto.replace("://",""),
                r.status_code,
                size,
                title,
                framework
            ])

        found = True

    return found


# load domains
with open("w.txt") as f:
    domains = list(set([x.strip() for x in f if x.strip()]))

print(f"[INFO] Domains loaded: {len(domains)}")
print(f"[INFO] Threads: {threads}")
print(f"[INFO] Delay: {delay}")

if args.proxy:
    print(f"[INFO] Proxy: {args.proxy}")

if proxy_list:
    print(f"[INFO] Proxy list loaded: {len(proxy_list)}")


with open("framework3.csv", "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)
    writer.writerow([
        "domain",
        "protocol",
        "status",
        "size",
        "title",
        "framework"
    ])

    with ThreadPoolExecutor(max_workers=threads) as executor:

        list(tqdm(
            executor.map(scan, domains),
            total=len(domains)
        ))
