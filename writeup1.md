# **boot2root**

## Table of content

- [**boot2root**](#boot2root)
  - [Table of content](#table-of-content)
  - [Introduction](#introduction)
  - [Finding the IP Address](#finding-the-ip-address)
  - [Enumeration](#enumeration)


## Introduction

This Hive Helsinki Project is about finding ways to gain root access on the boot2root virtual machine. Check the subject [file](https:linkmissing) for more information.

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

TODO: Insert Image http_landing_page here

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
