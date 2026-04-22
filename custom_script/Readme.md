# Remote Desktop Login Alert via Telegram

Panduan ini menjelaskan cara membuat **notifikasi Telegram otomatis** ketika seseorang melakukan login melalui **Remote Desktop (RDP)** pada Windows menggunakan **PowerShell**.

Script akan membaca **Windows Event Log** dan mengirim pesan ke **Telegram Bot API**.

---

# Prerequisites

Pastikan beberapa komponen berikut sudah tersedia:

- Telegram **Bot API Token**
- Telegram **Chat ID**
- **PowerShell 3 atau lebih baru**
- **Windows 10 / Windows Server**
- Akses internet dari server

---

# PowerShell Script

Buat file bernama:

```

rd_alert.ps1

````

Isi script berikut:

```powershell
# Telegram API settings
$apiToken = "YOUR_API_TOKEN"
$chatId = "YOUR_CHAT_ID"

# Remote Desktop login event ID
$eventId = 1149

$params = @{
  FilterHashtable = @{
    LogName = "Security"
    ID = $eventId
  }
}

function Send-TelegramAlert {
    param ($message)

    $uri = "https://api.telegram.org/bot$apiToken/sendMessage?chat_id=$chatId&text=$message"
    Invoke-WebRequest -Uri $uri -Method Post
}

Get-WinEvent @params | ForEach-Object {

    $username = $_.Properties[1].Value
    $message = "Remote Desktop login detected: $username"

    Send-TelegramAlert -message $message
}
````

---

# Script Configuration

Edit bagian berikut:

```
$apiToken = "YOUR_API_TOKEN"
$chatId = "YOUR_CHAT_ID"
```

Isi dengan:

* **Telegram Bot API Token**
* **Telegram Chat ID**

---

# Scheduling the Script

Agar script berjalan otomatis ketika terjadi login RDP:

1. Buka **Task Scheduler**
2. Pilih **Create Task**
3. Pada tab **Trigger**

```
Begin the task: On an event
Log: Security
Event ID: 1149
```

4. Pada tab **Action**

Program:

```
powershell.exe
```

Argument:

```
-File C:\Path\To\rd_alert.ps1
```

Sesuaikan dengan lokasi script.

---

# Testing

Untuk menguji script:

1. Login ke mesin Windows menggunakan **Remote Desktop**
2. Periksa Telegram
3. Jika berhasil, bot akan mengirim pesan seperti:

```
Remote Desktop login detected: Administrator
```

---

# Event ID Reference

## Windows Server

| Event ID | Description                       |
| -------- | --------------------------------- |
| 1149     | Remote Desktop connection attempt |
| 21       | Terminal Services user logon      |

Biasanya digunakan:

```
1149
```

---

## Windows 10 / Windows 11

Gunakan Event ID:

```
21
```

Script dapat diubah menjadi:

```powershell
$params = @{
  FilterHashtable = @{
    LogName = "Security"
    ID = 21
  }
}
```

---

# Execution Policy

Jika script tidak bisa dijalankan:

```
Set-ExecutionPolicy RemoteSigned
```

Jalankan PowerShell sebagai **Administrator**.

