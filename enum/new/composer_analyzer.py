import json
import sqlite3
import requests
import os
import glob
import csv
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from tqdm import tqdm

DOWNLOAD_DIR = "downloads"
DB_FILE = "composer_vulnerabilities.db"
CSV_FILE = "composer_vulnerabilities.csv"

########################################
# DATABASE
########################################

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS vulnerabilities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        package TEXT,
        installed_version TEXT,
        advisory_id TEXT,
        severity TEXT,
        vulnerable_versions TEXT,
        title TEXT,
        reference TEXT,
        UNIQUE(domain,package,installed_version,advisory_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS scan_progress(
        domain TEXT PRIMARY KEY,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


########################################
# CHECK PROGRESS
########################################

def domain_done(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    r = c.execute("SELECT status FROM scan_progress WHERE domain=?", (domain,)).fetchone()
    conn.close()
    return r and r[0] == "done"

def mark_running(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO scan_progress(domain,status) VALUES(?,?)", (domain,"running"))
    conn.commit()
    conn.close()

def mark_done(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE scan_progress SET status='done' WHERE domain=?", (domain,))
    conn.commit()
    conn.close()


########################################
# PARSE FILE NAME
########################################

def get_domain(filename):
    base = os.path.basename(filename)
    return base.replace("_composer.lock","").replace("_composer.json","")


########################################
# PARSE LOCK
########################################

def parse_lock(file):
    packages = []
    with open(file,"r",encoding="utf-8",errors="ignore") as f:
        data = json.load(f)
    for p in data.get("packages",[]):
        name = p["name"]
        version = p["version"].replace("v","")
        packages.append((name,version))
    for p in data.get("packages-dev",[]):
        name = p["name"]
        version = p["version"].replace("v","")
        packages.append((name,version))
    return packages


########################################
# PARSE JSON
########################################

def parse_json(file):
    packages = []
    with open(file,"r",encoding="utf-8",errors="ignore") as f:
        data = json.load(f)
    for name,ver in data.get("require",{}).items():
        packages.append((name,ver))
    for name,ver in data.get("require-dev",{}).items():
        packages.append((name,ver))
    return packages


########################################
# QUERY ADVISORY
########################################

def query_advisories(package):
    url = f"https://packagist.org/api/security-advisories/?packages[]={package}"
    try:
        r = requests.get(url,timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("advisories",{}).get(package,[])
    except:
        return []


########################################
# VERSION CHECK
########################################

def is_vulnerable(installed,constraint):
    try:
        spec = SpecifierSet(constraint)
        return Version(installed) in spec
    except:
        return False


########################################
# SAVE RESULT
########################################
def save_result(domain,pkg,ver,adv):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ambil CVE / GHSA / fallback
    cve = adv.get("cve") or adv.get("advisoryId") or "No known CVE"

    c.execute("""
    INSERT OR IGNORE INTO vulnerabilities
    (domain,package,installed_version,advisory_id,severity,vulnerable_versions,title,reference)
    VALUES(?,?,?,?,?,?,?,?)
    """,(
        domain,
        pkg,
        ver,
        cve,
        adv.get("severity",""),
        adv.get("affectedVersions",""),
        adv.get("title",""),
        adv.get("link","")
    ))

    conn.commit()
    conn.close()


########################################
# SCAN FILE
########################################

def scan_file(file):
    domain = get_domain(file)
    if domain_done(domain):
        print(f"Skipping {domain} (already scanned)")
        return
    mark_running(domain)
    print(f"\nScanning {domain}")
    if file.endswith(".lock"):
        packages = parse_lock(file)
    else:
        packages = parse_json(file)

    for pkg,ver in tqdm(packages):
        advisories = query_advisories(pkg)
        for adv in advisories:
            constraint = adv.get("affectedVersions","")
            if is_vulnerable(ver,constraint):
                save_result(domain,pkg,ver,adv)

    mark_done(domain)


########################################
# EXPORT CSV
########################################

def export_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    rows = c.execute("""
    SELECT domain, package, installed_version, advisory_id, severity, vulnerable_versions, title, reference
    FROM vulnerabilities
    ORDER BY domain, package
    """).fetchall()
    conn.close()

    with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain","Package","Installed Version","CVE / Advisory","Severity","Affected Versions","Title","Reference"])
        writer.writerows(rows)

    print(f"\nCSV exported: {CSV_FILE}")


########################################
# MAIN
########################################

def main():
    init_db()

    lock_files = glob.glob(f"{DOWNLOAD_DIR}/*_composer.lock")
    json_files = glob.glob(f"{DOWNLOAD_DIR}/*_composer.json")

    print(f"Found {len(lock_files)} lock files")
    print(f"Found {len(json_files)} json files")

    for f in lock_files:
        scan_file(f)

    for f in json_files:
        lock_equivalent = f.replace(".json",".lock")
        if not os.path.exists(lock_equivalent):
            scan_file(f)

    # export CSV setelah selesai scan
    export_csv()


if __name__ == "__main__":
    main()
