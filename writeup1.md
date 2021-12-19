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

## Enumeration