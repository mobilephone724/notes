---
title: "Number of Reversed Inode"
date: 2024-08-03T17:13:10+08:00
---

## 0x0 what is inode

From https://en.wikipedia.org/wiki/Inode

> The **inode** (index node) is a [data structure](https://en.wikipedia.org/wiki/Data_structure) in a [Unix-style file system](https://en.wikipedia.org/wiki/Unix_filesystem) that describes a [file-system](https://en.wikipedia.org/wiki/File_system) object such as a [file](https://en.wikipedia.org/wiki/Computer_file) or a [directory](https://en.wikipedia.org/wiki/Directory_(computing)). Each inode stores the attributes and disk block locations of the object's data

From https://www.redhat.com/sysadmin/inodes-linux-filesystem

> By definition, an inode is an index node. It serves as a unique identifier for a specific piece of metadata on a given filesystem. Each piece of metadata describes what we think of as a file. That's right, inodes operate on each filesystem, independent of the others.

Once you create a file, directory and so on, an inode is consumed. So it’s important to remain enough inodes.

## 0x1 **How many inodes are there?**

The inode upper limit is determined once the filesystem is initialized.

For ext4, there are two method to appoint the number

1. `bytes-per-inode` : 
   1. This is the default method to determine the number of inodes. 
   2. This option approves an method to help estimate the inodes you may need through the average file size. `mke2fs` creates an inode for every `bytes-per-inode` bytes of space on the disk. The larger the *bytes-per-inode* ratio, the fewer inodes will be created.
   3. The default value is 16k.
      1. If you create too many 8k files, the inode will run out before the disk space. So the disk space is wasted
      2. If you create too many 32k files, the disk space will run out before the inode. So the inode is wasted
2. `number-of-inodes` : Overrides the default calculation of the number of inodes that should be reserved for the filesystem.

See https://wiki.archlinux.org/title/Ext4 for detail