```html
<div style="font-family:Arial, Helvetica, sans-serif; background:#eef2f7; padding:30px;">

<div style="max-width:900px;margin:auto;background:white;padding:30px;border-radius:6px;box-shadow:0 3px 12px rgba(0,0,0,0.15);">

<h1 style="color:#0b3d91;">SecureBank Internal Security Training Portal</h1>

<p>
Portal ini dibuat untuk keperluan <b>Security Awareness Training</b> dan 
<b>Web Application Penetration Testing Practice</b>.  
Beberapa modul di bawah mensimulasikan kerentanan keamanan yang umum ditemukan
pada aplikasi web perbankan.
</p>

<hr>

<h2>Available Training Modules</h2>

<div style="background:#f5f7fa;padding:15px;border-left:5px solid #0b3d91;margin-top:20px;">
<h3>1. File Upload Vulnerability</h3>

<p>
Simulasi proses upload dokumen KYC nasabah.  
Pada modul ini terdapat kelemahan validasi file upload yang memungkinkan attacker
mengunggah file berbahaya ke server.
</p>

<p>
<a href="http://192.168.88.54/upload-lab/" style="font-weight:bold;color:#0b3d91;">
Open Upload Lab →
</a>
</p>
</div>

<div style="background:#f5f7fa;padding:15px;border-left:5px solid #0b3d91;margin-top:20px;">
<h3>2. Cross-Site Scripting (XSS)</h3>

<p>
Simulasi halaman profil nasabah yang menampilkan input pengguna tanpa sanitasi.
Kerentanan ini dapat dimanfaatkan attacker untuk menjalankan JavaScript berbahaya
atau mencuri cookie sesi pengguna.
</p>

<p>
<a href="http://192.168.88.54/xss-lab/" style="font-weight:bold;color:#0b3d91;">
Open XSS Lab →
</a>
</p>
</div>

<div style="background:#f5f7fa;padding:15px;border-left:5px solid #0b3d91;margin-top:20px;">
<h3>3. SQL Injection</h3>

<p>
Simulasi fitur pencarian akun nasabah yang melakukan query database tanpa
menggunakan prepared statement.  
Attacker dapat memanipulasi query SQL untuk membaca data sensitif dari database.
</p>

<p>
<a href="http://192.168.88.54/sqli-lab/" style="font-weight:bold;color:#0b3d91;">
Open SQL Injection Lab →
</a>
</p>
</div>

<hr>

<h2>Disclaimer</h2>

<p>
Halaman ini berisi simulasi kerentanan keamanan yang dibuat secara sengaja
untuk tujuan pembelajaran.  
Jangan gunakan teknik yang dipelajari di lingkungan produksi tanpa izin resmi.
</p>

</div>
</div>

```
