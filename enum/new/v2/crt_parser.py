import re
import argparse

parser = argparse.ArgumentParser(description="Extract domains from crt.sh HTML file")
parser.add_argument("domain", help="Target domain (example: desa.id)")
parser.add_argument("-f", "--file", default="crt.html", help="HTML file from crt.sh (default: crt.html)")

args = parser.parse_args()

file_html = args.file
target = args.domain

domains = set()

with open(file_html, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# regex cari domain
matches = re.findall(r"[a-zA-Z0-9_\-\.]+\." + re.escape(target), html)

for m in matches:
    m = m.replace("*.", "")
    domains.add(m.lower())

for d in sorted(domains):
    print(d)
