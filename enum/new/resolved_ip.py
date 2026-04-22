import socket
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

domains = set()
results = []
failed = []
lock = Lock()


# ambil semua domain dari folder
for root, dirs, files in os.walk("."):
    for name in ["findomain.txt", "subfinder.txt"]:
        path = os.path.join(root, name)
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    d = line.strip()
                    if d:
                        domains.add(d)


def resolve(domain):
    try:
        ip = socket.gethostbyname(domain)

        with lock:
            results.append((ip, domain))

    except:
        with lock:
            failed.append(domain)


print(f"[+] Total domains loaded: {len(domains)}")


# resolve parallel
with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(resolve, domains)


# save resolved
with open("resolved.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["IP", "Domain"])

    for ip, domain in sorted(results):
        writer.writerow([ip, domain])


# save unresolved
with open("unresolved.txt", "w") as f:
    for d in sorted(failed):
        f.write(d + "\n")


# output terminal
print("\n[+] Resolved Domains\n")

current_ip = None

for ip, domain in sorted(results):
    if ip != current_ip:
        print(f"\n{ip}")
        print("-" * 40)
        current_ip = ip

    print(domain)


print(f"\n[+] Resolved: {len(results)}")
print(f"[+] Unresolved: {len(failed)}")
