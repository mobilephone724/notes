---
title: "pg_repack"
author: "mobilephone724"
math: true
---

## principle

[pg_repack 1.5.0 -- Reorganize tables in PostgreSQL databases with minimal locks](https://reorg.github.io/pg_repack/)

[https://github.com/reorg/pg_repack](https://github.com/reorg/pg_repack)

1. create a log table to record changes made to the original table
2. add a trigger onto the original table, logging INSERTs, UPDATEs and DELETEs into our log table
3. create a new table containing all the rows in the old table
4. build indexes on this new table
5. apply all changes which have accrued in the log table to the new table
6. swap the tables, including indexes and toast tables, using the system catalogs
7. drop the original table

The basic idea is

1. transport the existent data with a old snapshot
2. record the incremental data into a table and replay the record

And this idea is so general that almost all online-ddl ability in PG(supported in extensions) takes the way.

## details

Although the idea is so simple, there are many problems to challenge. Such as how to ensure there are no duplicated or lost data in both existent part and incremental part. So code-level details are shown below:

All the 7 step are manipulated through 2 connections: See function `repack_one_table` for detail:

1. create a log table to record changes made to the original table

2. add a trigger onto the original table, logging INSERTs, UPDATEs and DELETEs into our log table

   1.  `conn1` starts a transaction and acquire an [advisory lock](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS) to prevent potential conflict with other repack process
   2.  get the `AccessiveExclusive` lock to the original table, `tbl` for example
   3.  create the trigger on `tbl` and the corresponding  `log-table` where the incremental changes will be stored.
   4.  (Just comments: If we release the exclusive lock here, we may not able to acquire a shared lock later if another process has gotten a exclusive lock in the interval, which can cause that we have no way to continue or revert what we have done. So we must acquire a lock during the whole process. 👌)
   5.  `conn2` tries to acquire the `AccessiveShared` lock on `tbl`. Since the `conn1` 's transaction hasn't finished, this lock acquisition will be blocked.
   6.  `conn1` kill all connections that tries to perform a DDL operation, whose character is waiting for `AccessiveLock` . Then, `conn1` commits. 
   7.  Now `conn2` get the `AccessiveShared` lock on `tbl` , which can ensure that no other dll operation on `tbl` ✌️

3. create a new table containing all the rows in the old table

   1. `conn1` begins a serializable transaction( repeatable read, at least)

   2. `conn1` get the `vxids` of current active transactions

   3. `conn1` delete all data in `tbl` with the current snapshot (This means we don't perform a “truncate” operation ). This is a very skillful technique:

      1. **The table shows the secret:**


         |           | tbl              | log table        |
         | --------- | ---------------- | ---------------- |
         | visible   | existent data    | empty            |
         | invisible | incremental data | incremental data |

      2. All existent data is visible in `tbl` through the current snapshot

      3. All incremental data is invisible in `log table` and `tbl` (The latter one isn't important

      4. So there is no lost or duplicated data

   4. `conn1` copies all data in `tbl` to a temp table `tbl-tmp`  for example

   5. `conn1` commits

4. build indexes on this new table. (I don't care this.)

5. apply all changes which have accrued in the log table to the new table

   1. `conn1` apply at most 1000 records in `log-table` , until
      1. the remaining records are few. AND
      2. All transactions in `vxids` finish. This operation is to keep the ISOLATION, but it still has some accidence. #TODO 
   2. (Just comments: Now we believe that there is few records in `log-table` .)
   3. `conn2` acquire the `AccessiveExclusive` lock. Note that no other process can do that
   4. `conn2` apply all data in `log-table`

6. swap the tables, including indexes and toast tables, using the system catalogs

   1. `conn2` swaps `relfilenode` between `tbl-tmp` and `tbl`
   2. `conn2` commits

7. drop the original table

   1. `conn1` drop the current `tbl-tmp`
   2. `conn1` analyze the current `tbl`
   3. `conn1` release the advisory lock