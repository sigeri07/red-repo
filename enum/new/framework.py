import requests
import re
import urllib3
import csv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

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

def scan(domain):

    for proto in ["http://", "https://"]:

        url = proto + domain

        try:

            r = requests.get(
                url,
                timeout=5,
                verify=False,
                headers=headers
            )

            title = get_title(r.text)
            framework = detect_framework(r)

            output = f"[{r.status_code}] {url}"

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
                    title,
                    framework
                ])

        except:
            pass


with open("w.txt") as f:
    domains = [x.strip() for x in f if x.strip()]


with open("framework.csv", "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.writer(csvfile)
    writer.writerow(["domain","protocol","status","title","framework"])

    with ThreadPoolExecutor(max_workers=80) as executor:
        executor.map(scan, domains)
