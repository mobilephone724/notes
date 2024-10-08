---
title: WAL基础
author: mobilephone724
math: true
next: /database/wal/insert
---
> From `access/transam/README`

## Write-Ahead Log Coding

基本思想，日志在数据页前落盘

1. `LSN`：刷脏前检查`LSN`对应的日志已经落盘
    1. 优势：仅在必要的时候等待`XLOG`的`IO`。（异步`IO`）
    2. `LSN`的检查模块只用在 buffer manager 中实现
    3. 在WAL回放时，避免相同的日志被重复回放（可重入）。（TODO：full page write是否在另一个层面上保证了可重入）
2. WAL 包含一个（或一小组）页的**增量更新**的重做信息。
    1. 依赖文件系统和硬件的原子写，不可靠！
    2. checkpoint，checkpointer后的第一次写全页。通过 checkpoint 留下的 `LSN ` 来判断是否为第一次写
3. 写下WAL日志的逻辑为
    1. pin and exclusive-lock the shared buffer 
    2. START_CRIT_SECTION，发生错误时确保整个数据库能立即重启
    3. 在shared buffer上，进行对应的修改
    4. 标记为脏页，
        1. 必须在WAL日志写入前完成（TODO，为什么？`SyncOneBuffer`）
        2. 只有在要写WAL时，才能标记脏页（TODO，为什么？）
    5. 使用`XLogBeginInsert` 和 `XLogRegister*` 函数构建WAL，使用返回的`LSN`来更新`page`
    6. END_CRIT_SECTION，退出
    7. 解锁和unpin （注意顺序）

一些复杂的操作，需要原子地写下一串WAL记录，但中间状态必须自洽(self-consistent)。这样在回放wal日志时，如果中断，系统还能够正常运行。注意：此时相当于事务回滚，但是其部分更改已经落盘。举例：
* 在btree索引中，页的分裂分为两步（1）分配一个新页（2）在上一层的页(parent page)中新插入一条数据。
* 但是因为锁，这会形成两个独立的WAL日志。在回放WAL日志时
    * 回放第（1）个日志：
        * 分配一个新页，将元组移动进去
        * 设置标记位，表示上一层的页没有更新
    * 回放第（2）个日志：
        * 在上一层的页中新插入一条数据
        * 清除第（1）个日志中的标记位
* 标志位通常情况下不可见，因为对 child page 的修改时持有的锁，在两个操作完成后才会释放。
* 仅在写下第（2）个日志前，数据库恰好崩溃，标志位才会被感知。（该标志位应该没有MVCC，否则会在事务层屏蔽）
    * 搜索时，不管这个中间状态
    * 插入时，如果发现这个中间状态，先在上一层的页插入对应key，以修复这个“崩溃”状态，再继续插入

