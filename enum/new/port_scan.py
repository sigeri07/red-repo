import socket
import csv
from concurrent.futures import ThreadPoolExecutor

ports = [80, 443, 8080]
timeout = 3

results = []


def check_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)

        if s.connect_ex((ip, port)) == 0:
            print(f"[OPEN] {ip}:{port}")
            results.append([ip, port, "open"])

        s.close()

    except:
        pass


def worker(ip):
    for port in ports:
        check_port(ip, port)


with open("ip.txt") as f:
    ips = [x.strip() for x in f if x.strip()]


with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(worker, ips)


# save ke CSV
with open("port_scan.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["IP", "Port", "Status"])
    writer.writerows(results)
