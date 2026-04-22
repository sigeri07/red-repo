```bash
└─$ sudo apt install systemd-timesyncd
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following package was automatically installed and is no longer required:
  python3-ntp
Use 'sudo apt autoremove' to remove it.
The following packages will be REMOVED:
  ntpsec
The following NEW packages will be installed:
  systemd-timesyncd
0 upgraded, 1 newly installed, 1 to remove and 0 not upgraded.
Need to get 67.5 kB of archives.
After this operation, 763 kB disk space will be freed.
Do you want to continue? [Y/n]
Get:1 http://192.168.88.97/kali 2023.4/main amd64 systemd-timesyncd amd64 254.5-1 [67.5 kB]
Fetched 67.5 kB in 1s (104 kB/s)
(Reading database ... 421157 files and directories currently installed.)
Removing ntpsec (1.2.2+dfsg1-2) ...
Selecting previously unselected package systemd-timesyncd.
(Reading database ... 421119 files and directories currently installed.)
Preparing to unpack .../systemd-timesyncd_254.5-1_amd64.deb ...
Unpacking systemd-timesyncd (254.5-1) ...
Setting up systemd-timesyncd (254.5-1) ...
Created symlink /etc/systemd/system/dbus-org.freedesktop.timesync1.service → /lib/systemd/system/systemd-timesyncd.service.
Created symlink /etc/systemd/system/sysinit.target.wants/systemd-timesyncd.service → /lib/systemd/system/systemd-timesyncd.service.
Processing triggers for man-db (2.12.0-1) ...
Processing triggers for dbus (1.14.10-3) ...
Processing triggers for kali-menu (2023.4.6) ...

┌──(kali㉿kali)-[~]
└─$ sudo timedatectl set-ntp off
└─$ sudo rdate -n 10.129.5.181 ; bloodhound-python -c All -u pentest -p 'p3nt3st2025!&' -d pirate.htb -ns 10.129.5.181
[sudo] password for kali:


Tue Mar 17 08:00:18 EDT 2026
INFO: Found AD domain: pirate.htb
INFO: Getting TGT for user
INFO: Connecting to LDAP server: dc01.pirate.htb
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 6 computers
INFO: Connecting to LDAP server: dc01.pirate.htb
INFO: Found 10 users
INFO: Found 54 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 20 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: adfs.pirate.htb
INFO: Querying computer: adcs.pirate.htb
INFO: Querying computer:
INFO: Querying computer:
INFO: Querying computer: WEB01.pirate.htb
INFO: Querying computer: DC01.pirate.htb
WARNING: Could not resolve: adfs.pirate.htb: The resolution lifetime expired after 3.210 seconds: Server Do53:10.129.5.181@53 answered The DNS operation timed out.; Server Do53:10.129.5.181@53 answered The DNS operation timed out.
WARNING: Could not resolve: adcs.pirate.htb: The resolution lifetime expired after 3.212 seconds: Server Do53:10.129.5.181@53 answered The DNS operation timed out.; Server Do53:10.129.5.181@53 answered The DNS operation timed out.
INFO: Done in 00M 05S

```
