---
title: "pg_squeence_type"
date: 2024-02-12T19:51:45+08:00
---

# sequence type

# background

From official documents:

[9.17. Sequence Manipulation Functions](https://www.postgresql.org/docs/16/functions-sequence.html)

[CREATE SEQUENCE](https://www.postgresql.org/docs/current/sql-createsequence.html)

* Sequence objects **are special single-row tables** created with **[CREATE SEQUENCE](https://www.postgresql.org/docs/16/sql-createsequence.html)**.
* Sequence objects are commonly used to generate unique identifiers for rows of a table. The sequence functions, provide simple, multiuser-safe methods for obtaining successive sequence values from sequence objects.

# Main function

There is no much concerns about these functions

* `nextval`

    * Advances the sequence object to its next value and returns that value

* `setval`

    * Some examples

        | SELECT setval('myseq', 42);        | Next nextval will return 43 |
        | ---------------------------------- | --------------------------- |
        | SELECT setval('myseq', 42, true);  | Same as above               |
        | SELECT setval('myseq', 42, false); | Next nextval will return 42 |

* `currval`

    * Returns the value most recently obtained by `nextval` for this sequence **in the current session**

* `lastval`

    * Returns the value most recently returned by `nextval` in the current session. This function is identical to `currval`, except that instead of taking the sequence name as an argument it refers to whichever sequence `nextval` was most recently applied to in the current session.

-------



** There is a caution: ** 

There is no rollback of the `sequence` type. Official document is post below:

To avoid blocking concurrent transactions that obtain numbers from the same sequence, the value obtained by `nextval` is not reclaimed for re-use if the calling transaction later aborts. This means that transaction aborts or database crashes can result in gaps in the sequence of assigned values. That can happen without a transaction abort, too. For example an `INSERT` with an `ON CONFLICT` clause will compute the to-be-inserted tuple, including doing any required `nextval` calls, before detecting any conflict that would cause it to follow the `ON CONFLICT` rule instead. Thus, PostgreSQL sequence objects *cannot be used to obtain “gapless”（无缝的） sequences*.

# Most important

All things above doesn’t worth a post, but the replication hack of this type does. Considering a master-standby example, the `currval` in standby is always bigger than the master's. And once the value in master advances and the new value doesn't precede the standby's one, the `currval` in standby would't advanced immediately. This is a greate skill to reduce the wal records.
