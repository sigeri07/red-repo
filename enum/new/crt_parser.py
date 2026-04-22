import re

file_html = "crt.html"   # file hasil save dari crt.sh
target = "esdm.go.id"

domains = set()

with open(file_html, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# cari domain yang mengandung target
matches = re.findall(r"[a-zA-Z0-9_\-\.]+\." + re.escape(target), html)

for m in matches:
    m = m.replace("*.", "")
    domains.add(m.lower())

for d in sorted(domains):
    print(d)
