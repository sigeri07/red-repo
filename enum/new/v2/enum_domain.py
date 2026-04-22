import argparse
import sqlite3
import subprocess
import os
from datetime import datetime

DB_FILE = "c:\pentest\subdomains.db"


########################################
# DATABASE
########################################

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        domain TEXT PRIMARY KEY,
        last_scan TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS subdomains (
        domain TEXT,
        subdomain TEXT,
        source TEXT,
        UNIQUE(subdomain)
    )
    """)

    conn.commit()
    conn.close()


########################################
# CHECK DOMAIN
########################################

def already_scanned(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT domain FROM domains WHERE domain=?", (domain,))
    result = c.fetchone()

    conn.close()

    return result is not None


########################################
# UPDATE DOMAIN
########################################

def update_domain(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    c.execute("""
    INSERT OR REPLACE INTO domains(domain,last_scan)
    VALUES(?,?)
    """, (domain, now))

    conn.commit()
    conn.close()


########################################
# SAVE SUBDOMAINS
########################################

def save_subdomains(domain, file, source):

    if not os.path.exists(file):
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    with open(file) as f:
        for line in f:
            sub = line.strip()
            if sub:
                try:
                    c.execute(
                        "INSERT OR IGNORE INTO subdomains(domain,subdomain,source) VALUES(?,?,?)",
                        (domain, sub, source)
                    )
                except:
                    pass

    conn.commit()
    conn.close()


########################################
# RUN COMMAND
########################################

def run_cmd(cmd):
    subprocess.run(cmd, shell=True)


########################################
# ENUMERATION
########################################

def enum_domain(domain):

    print("\n--------------------------------")
    print("[TARGET]", domain)

    if not os.path.exists(domain):
        os.mkdir(domain)
        print("[DIR] Created", domain)

    findomain_file = f"{domain}/findomain.txt"
    subfinder_file = f"{domain}/subfinder.txt"

    # FINDOMAIN
    if os.path.exists(findomain_file):
        print("[SKIP] findomain exists")
    else:
        print("[RUN] findomain")
        run_cmd(f"findomain -t {domain} -q > {findomain_file}")
        print("[OK] saved", findomain_file)

    # SUBFINDER
    if os.path.exists(subfinder_file):
        print("[SKIP] subfinder exists")
    else:
        print("[RUN] subfinder")
        run_cmd(f"subfinder -d {domain} -all -recursive -silent -o {subfinder_file}")
        print("[OK] saved", subfinder_file)

    # SAVE RESULTS
    save_subdomains(domain, findomain_file, "findomain")
    save_subdomains(domain, subfinder_file, "subfinder")

    # UPDATE DB
    update_domain(domain)

    print("[DB] updated")


########################################
# MAIN
########################################

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", default="d.txt")
    parser.add_argument("--override", action="store_true")

    args = parser.parse_args()

    init_db()

    if not os.path.exists(args.list):
        print("domain list not found")
        return

    with open(args.list) as f:

        for domain in f:

            domain = domain.strip()

            if not domain:
                continue

            if already_scanned(domain) and not args.override:
                print("[SKIP] already scanned:", domain)
                continue

            enum_domain(domain)


if __name__ == "__main__":
    main()
