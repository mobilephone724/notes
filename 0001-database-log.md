---
title: "Basic Knowledge of Database Log"
author: "mobilephone724"
toc:
 enable: true
 auto: true
date: 2022-03-31T11:01:15+08:00
publishDate: 2022-03-31T11:01:15+08:00
---

## Primitive Operation if Transactions
There are `three address spaces` that transaction interact in important ways:
1.	The space of **disk blocks** holding the database elements.
2.	The **memory address space** managed by buffer manager.
3.	The **local address space** of the transaction.

To describe a transaction, we need some `operation notions`:(X below is a database element while t is a local varible, and we suppose a database element is no larger than a single block)
1.	INPUT(X): copy disk block containing X to memroy buffer
2.	READ(X, t): Copy X to transaction's local varible t no matter where X is, which means INPUT(X) may be executed first before READ(X,t).
3.	WRITE(X, t): Copy the value of t to X no matter where X is.
4.	OUTPUT(X): Copy the block containing X from its buffer to disk

## undo logging

Undo log makes repairs to the database state by undoing the effects of transactions that may not completed before the crash.

An Undo log has the form [T,X,v] which means transaction T has changed the database elememnt X, and its before value was v. The log record is a response to a WRITE action into memory, not an OUTPUT action.

An undo log is suffcient to allow recovery from system failure, provided transactions and buffer manager obey two rules:
1.	If transaction T modifies database element X, then the log record of form <T,X,v> must be written to disk before the new value of X is written to disk
2.	If a transaction commits, the its commit log record must be written to disk only after all database elements changed by the transaction have been written to disk, but as soon there after is possible
3.	If a transaction aborts, recovery manager is need to repair the values.

When recovering, the recovery manager scan the log from the end. As it travels, it remembers all thos transactions T for which it has seen a [COMMIT T] record or [ABORT T] record, the:
1.	If T's COMMIT record is found, do nothing.
2.	Otherwise, T is an incomplete transaction, or aborted transaction. The recovery manager must change the value of X in the database to v,in case X had been altered just before the crash. After this, the recovery manager must write a log record [ABORT T] for each incomplete transaction T that was not previously aborted, and then flush the log