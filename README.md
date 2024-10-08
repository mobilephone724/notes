# Intro
This repo is copied from my hugo blog. It takes much time to maintain that since:

1. I want to consider the url stability of a post.
2. The post organization costs too much time.
3. The related asserts organization is too strick.

So just keeping these posts readable in github with markdown format seems a good choice.

The format of the repo:
1. Every new notes **must** be prefixed with a 4-length serial number generated from `./nextd.sh`
2. New assets **must** be in the `/assets` directory and prefixed like `${4-length notes prefixed}-${3-length image prefixed}-xxx.suffix`

Directory hierarchy may not be perfect for linking???
# TODO
- [ ] Relationship storage in Neo4j

## Linux Related

- [0006-linux-file](0006-linux-file.md)
- [0008-reversed_inode](0008-reversed_inode.md)
- [0030-intro-to-io-uring](0030-intro-to-io-uring.md)

## Database Related

- Paper Reading
    - [0003-google-f1](0003-google-f1.md)
    - [0026-20years-database](0026-20years-database.md)
    - [0027-constant_recovery](0027-constant_recovery.md)
 - PostgreSQL
    - SLRU Related
        - [0020-slru](0020-slru.md)
        - [0021-clog](0021-clog.md)
    - WAL Related
        - [0022-wal-basic](0022-wal-basic.md)
        - [0023-wal-insert](0023-wal-insert.md)
    - Index Related
        - [0025-hot-and-create-index](0025-hot-and-create-index.md)
    - Online Scheme Change
        - [0014-column-schema-change](0014-column-schema-change.md)
        - [0028-pg_repack](0028-pg_repack.md)
        - [0025-hot-and-create-index](0025-hot-and-create-index.md)
    - others:
        - [0013-build_from_source](0013-build_from_source.md)
        - [0016-hashjoin](0016-hashjoin.md)
        - [0015-every_data_pg](0015-every_data_pg.md)
        - [0017-pgvector](0017-pgvector.md)
        - [0018-sequence_type](0018-sequence_type.md)
        - [0019-ssl-in-PG](0019-ssl-in-PG.md)
- others
    - [0001-database-log](0001-database-log.md)

## Miscellaneous

- [0002-fwrapv](0002-fwrapv.md)
- [0005-howToKnowWhoseIsBigger](0005-howToKnowWhoseIsBigger.md)
- [0007-zero2rsa](0007-zero2rsa.md)
- [0009-cublasdgemmtutor](0009-cublasdgemmtutor.md)
- [0029-link-time-optimization](0029-link-time-optimization.md)
- [0011-roaring-bitmap](0011-roaring-bitmap.md)
- [0012-mesi](0012-mesi.md)