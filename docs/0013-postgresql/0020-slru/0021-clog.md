---
title: CLOG
author: mobilephone724
math: true
weight: 2
prev: /database/pg_xact/slru/slru
---

## Overview
This chapter explains the content of `clog`

`clog`(commit log), records the commit status of each transaction. The log
exists both in memory mannaged by `slru` buffer and disk for durability. The
commit status can be the four kinds below:
```C
#define TRANSACTION_STATUS_IN_PROGRESS		0x00
#define TRANSACTION_STATUS_COMMITTED		0x01
#define TRANSACTION_STATUS_ABORTED			0x02
#define TRANSACTION_STATUS_SUB_COMMITTED	0x03
```




## In-Disk Representation
Thinking that the commit status of each transaction composites an array `clog[]`
and `clog[xid]` records the status, we can easily store the array to disk by the
`slru`.

The status of one transaction needs two bits to represent:
```C
#define CLOG_BITS_PER_XACT	2
#define CLOG_XACTS_PER_BYTE 4
#define CLOG_XACTS_PER_PAGE (BLCKSZ * CLOG_XACTS_PER_BYTE)
#define CLOG_XACT_BITMASK	((1 << CLOG_BITS_PER_XACT) - 1)
```

So we can get the xid's index and offset in page and byte.
```C
#define TransactionIdToPage(xid)	((xid) / (TransactionId) CLOG_XACTS_PER_PAGE)
#define TransactionIdToPgIndex(xid) ((xid) % (TransactionId) CLOG_XACTS_PER_PAGE)
#define TransactionIdToByte(xid)	(TransactionIdToPgIndex(xid) / CLOG_XACTS_PER_BYTE)
#define TransactionIdToBIndex(xid)	((xid) % (TransactionId) CLOG_XACTS_PER_BYTE)
```

Thinking of that one slru segment contains 32 pages, so we name the clog file as
`0000`(contains xid in [0, 32 * CLOG_XACTS_PER_PAGE - 1]), `0001`(contains xid
in [32 * CLOG_XACTS_PER_PAGE, 32 * CLOG_XACTS_PER_PAGE * 2 - 1]) and so on.
Because four hex numbers can represent $16^4=2^{12}$ files with
$2^{12} \times 32 \times 8192 \times 4 = 2^{32}$ transactions' status(a int32 size)

Attension, such simple mapping means that the pages in clog file don't have
page headers. So we can't record `LSN`, `checksum` in each page. The lack of
`LSN` means the changes of clog page wouldn't be recorded in `WAL` but clog
doesn't need it indeed.





## Extend And Truncate
During the process of generating a new `xid`, we make sure that the slru page
exists.
* If it's the first xid of the page, we allocate a new page in clog buffer.
  * Also generate a WAL to record the birth of the page.
* If not, the page must exist in memory or flushed into disk. So it's for slru
  layer to manage such situation.

Keep in mind that the general self-increment xid does't begin at zero:
```C
#define FirstNormalTransactionId	((TransactionId) 3)
```
so:
* During bootstrap, initialize the first clog page
* During extend new pages, be careful about the `FirstNormalTransactionId`,
  since it is not the first xid in page representation but the first general one.

The above behaviors indicate that although a clog segment at most occupies 256K
space, it doesn't have such size just after initialization. We extend 8K pages
one by one during the xid increment.

Since at most half of `uint32` xids can be in use, it's natural to clean up out
of date clog files. Different from extending a page, we always delete a whole
page. So once we promote the `frozenxid`, we try to find some clog files to
delete:
1. The judgement whether there is a file can be deleted is completed in slru
   layer(a loop to scan the directory), but clog layer supports a hook to judge
   one file.
2. Advance the oldest clog xid in shared memory
3. Generate a clog truncate WAL record
4. Real truncate. Complemented in slru layer.

Details of the two kind WAL record will be shown later.

## Set And Get
Concerned with subtransactions ...
> I can't totally figure out the commit tree without knowing the mechanism of
> subtransaction. Just assuming subxids as a set of xids related to the main xid
> seems not convictive enough for me. So I remain it here now and will finish it
> after reading subtransactions)

For now, it's enough to knowing that
1. The pair of operations wouldn't generate any WAL record
2. They are done during the commit or abort procedure.

## Record changes in WAL
Recall what mentioned above:
* Extending a new page and delete a segment will generata a WAL record.
* Setting commit status wouldn't

For the latter one, it's unbelievable but tricky. Since only the transactions
that changes the content data(some hint flags are exception, such as tuple
infomask) will have a xid(and then record on clog segment). During the replay of
such transactions' commit(or abort) WAL record, we can redo the clog by the way.

For the former one, it's a matter of course, since we must guarantee the clog to
be recovery-safe. But some details deserve a glance;
* For extending a new page, it makes no difference that we flush the WAL record
  now or later. Since once we want to set status in a non-existent page during
  recovery, we can padding a new empty page. This trick doesn't affect the page
  usage.
* For deleting a clog segment, we have no chance to remedy the lost of clogs,
  and the disaster means a lot of tuple can be accessed at all. So regardless of
  the synchronous commit level, we must ensure the WAL record has flushed into
  disk before really delete the segments.


