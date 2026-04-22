# WordPress Lab Setup

Dokumen ini berisi langkah-langkah untuk menyiapkan database WordPress dan script untuk mengubah URL WordPress secara otomatis.

---

# 1. Membuat User Database

Gunakan perintah SQL berikut untuk membuat user database dengan akses penuh.

```sql
CREATE USER 'dbadmin'@'%' IDENTIFIED BY 'P@ssw0rd';
GRANT ALL PRIVILEGES ON *.* TO 'dbadmin'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
````

### Penjelasan

| Command                | Deskripsi                                          |
| ---------------------- | -------------------------------------------------- |
| `CREATE USER`          | Membuat user database baru                         |
| `GRANT ALL PRIVILEGES` | Memberikan semua hak akses ke database             |
| `WITH GRANT OPTION`    | Mengizinkan user memberikan privilege ke user lain |
| `FLUSH PRIVILEGES`     | Memuat ulang privilege database                    |

---

# 2. Script Update URL WordPress

Script berikut digunakan untuk mengubah nilai `siteurl` dan `home` pada database WordPress.

File: `update_wp_url.sh`

```bash
#!/bin/bash

# Database configuration (modify these values as needed)
DB_USER="root"
DB_PASS=""
DB_NAME="wordpress"

# Check if IP address is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <new_site_url>"
  exit 1
fi

NEW_URL="$1"

# Execute MySQL commands to update siteurl and home
mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" <<EOF
UPDATE wp_options SET option_value = 'http://$NEW_URL' WHERE option_name = 'siteurl';
UPDATE wp_options SET option_value = 'http://$NEW_URL' WHERE option_name = 'home';
EOF

if [ $? -eq 0 ]; then
  echo "Successfully updated siteurl and home to http://$NEW_URL"
else
  echo "Failed to update the database. Please check the connection and credentials."
fi
```
