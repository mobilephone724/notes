See below structure
```C
typedef struct RelFileLocator
{
    Oid           spcOid;       /* tablespace */
    Oid           dbOid;        /* database */
    RelFileNumber relNumber;    /* relation */
} RelFileLocator;
```
* `RelFileNumber` is the file name of the relation
    * Oid of a relation is logically existent.
    * RelFileNumber is physically existent, since operations like `vacuum full` and `truncate` will create new files with different file name
* `ForkNumber`
    * It is the file "type" of a relation
        * The main data, fsm and vm are all bufferd by the [buffer](buffer.md)
    * `MAIN_FORKNUM` : heap file
    * `FSM_FORKNUM` : free space manager file
    * `VISIBILITYMAP_FORKNUM` : VISIBILITYMAP file
    * `INIT_FORKNUM` : for [unlogged table](https://www.postgresql.org/docs/current/sql-createtable.html#SQL-CREATETABLE-UNLOGGED)
> Data written to unlogged tables is **not written to the write-ahead log** which makes them considerably **faster** than ordinary tables. However, they are **not crash-safe**: an unlogged **table is automatically truncated** after a crash or unclean shutdown. The contents of an unlogged table are also **not replicated to standby servers**. Any indexes created on an unlogged table are automatically unlogged as well.





