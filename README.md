# Intro
This repo is copied from my hugo blog. It takes much time to maintain that since:

1. I want to consider the url stability of a post.
2. The post organization costs too much time.
3. The related asserts organization is too strick.

So just keeping these posts readable in github with markdown format seems a good choice.

The format of the repo:
1. Every new notes **must** be prefixed with a 4-length serial number generated from `./nextd.sh`
2. New assets **must** be in the `/assets` directory and prefixed like `${4-length notes prefixed}-${3-length image prefixed}-xxx.suffix`

# TODO
- [ ] Relationship storage in Neo4j


# Top Five Newest
```
./0000-computer_science/0029-link-time-optimization.md
./0013-postgresql/0024-index-in-pg/0025-hot-and-create-index.md
./0013-postgresql/0028-pg_repack.md
./0013-postgresql/0017-pgvector.md
./0013-postgresql/0016-hashjoin.md
```

# Directory Tree
```
.
├── 0000-computer_science
│   ├── 0001-database-log.md
│   ├── 0002-fwrapv.md
│   ├── 0005-howToKnowWhoseIsBigger.md
│   ├── 0006-linux-file.md
│   ├── 0007-zero2rsa.md
│   ├── 0008-reversed_inode.md
│   ├── 0009-cublasdgemmtutor.md
│   └── 0029-link-time-optimization.md
├── 0010-paper_reading
│   ├── 0003-google-f1.md
│   ├── 0011-roaring-bitmap.md
│   ├── 0012-mesi.md
│   ├── 0026-20years-database.md
│   └── 0027-constant_recovery.md
├── 0013-postgresql
│   ├── 0013-build_from_source.md
│   ├── 0014-column-schema-change.md
│   ├── 0015-every_data_pg.md
│   ├── 0016-hashjoin.md
│   ├── 0017-pgvector.md
│   ├── 0018-sequence_type.md
│   ├── 0019-ssl-in-PG.md
│   ├── 0020-slru
│   │   ├── 0020-slru.md
│   │   └── 0021-clog.md
│   ├── 0022-wal
│   │   ├── 0022-wal-basic.md
│   │   └── 0023-wal-insert.md
│   ├── 0024-index-in-pg
│   │   └── 0025-hot-and-create-index.md
│   └── 0028-pg_repack.md
├── assets
└── readme.md

8 directories, 27 files
```

In macos: I management my markdown docs with the structure like
```
subdir_path
\__ doc_1
    \__ assets (store images or other assets related to doc_1)
    \__ doc_1.md
    \__ doc_3 (optional)
        \__ assets
        \__ doc_3.md
        \__ may be more subdirs
\__ doc_2
    \__ assets
    \__ doc_2.md
    \__ may be more subdirs
\__ may be more subdirs
```

It is very convenient to move a single doc with its assets together. But when I 
want to (1) split a doc into others manually (2) merge some docs into one, I
need to update the paths of assets in the markdown files manually.

But luckily, I can confirm that all the image name in markdown files are unique,
so write me a script to update the paths of images in markdown files automatically
is easy.

What I want is like `refresh_img_path.py`, which scans all the markdown files in current
dictory and its subdirectories, find all the images used in these markdown files. If one
image is not found in the `assets` subdirectory of the markdown file, search it in the whole
repo, and copy the image to the `assets` subdirectory. I can ensure the image ref path in
markdown file is always `![](./asset/xxx)`
