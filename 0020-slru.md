---
title: SLRU
author: mobilephone724
math: true
weight: 1
next: /database/pg_xact/slru/clog
---
本文主要为`SLRU`本身的结构解读。

### 简述

+ slru用来干什么？
    + slru是一个简单的buffer管理模块，simple slru
+ 有了buffer pool manager，为什么还要slru？
    + bpm管理通用的page，比如heap，vm等
    + slru最大的特点就是lru，非常适合处理xid这样，递增的信息。
+ 下面的代码分析基于pg15

### 存储结构

与bpm不同，通过slru管理的page，其文件大小固定，一个文件有32个page，一个page有8KB，故一个文件最大为256K。

与WAL不同，WAL文件的大小在创建时就已经确定为16M，与WAL文件重用保持一致，而slru的文件，先在内存中产生相应的page，再会去落盘。

```C
#define SLRU_PAGES_PER_SEGMENT	32
```

####  内存slru

##### 全局 buffer 数组

```C
typedef struct SlruSharedData
{
	LWLock	   *ControlLock;

	/* Number of buffers managed by this SLRU structure */
	int			num_slots;

	/*
	 * Arrays holding info for each buffer slot.  Page number is undefined
	 * when status is EMPTY, as is page_lru_count.
	 */
	char	  **page_buffer;
	SlruPageStatus *page_status;
	bool	   *page_dirty;
	int		   *page_number;
	int		   *page_lru_count;
	LWLockPadded *buffer_locks;

    XLogRecPtr *group_lsn;
	int			lsn_groups_per_page;

	/*----------
	 * We mark a page "most recently used" by setting
	 *		page_lru_count[slotno] = ++cur_lru_count;
	 * The oldest page is therefore the one with the highest value of
	 *		cur_lru_count - page_lru_count[slotno]
	 * The counts will eventually wrap around, but this calculation still
	 * works as long as no page's age exceeds INT_MAX counts.
	 *----------
	 */
	int			cur_lru_count;
} SlruSharedData;
```

从内存结构上看，是一个数组，每个元素代表一个page。同时，记录这些page的使用次数。

```C
page_lru_count[slotno] = ++cur_lru_count;
```

同时每个page，都有状态标识，以在刷脏时，确定脏页。实际上这里没有脏页这个选项，因为只有 `valid` 状态的页才有可能是脏页，有包含关系。故在`SlruSharedData` 中使用 `page_dirty` 进行单独标识。

```C
typedef enum
{
	SLRU_PAGE_EMPTY,			/* buffer is not in use */
	SLRU_PAGE_READ_IN_PROGRESS, /* page is being read in */
	SLRU_PAGE_VALID,			/* page is valid and not being written */
	SLRU_PAGE_WRITE_IN_PROGRESS /* page is being written out */
} SlruPageStatus;
```
关于为什么需要记录LSN信息 `group_lsn`：这与 `WAL` 设计有关。对于 `WAL` 而言，无论是同步提交或是异步提交，都需要在对应的 `buffer page` 落盘前落盘,所以 `slru` 也需要满足这样的规则。同时，可能是为了节约内存（节约的内存实在有限），或是减少`WAL flush`的调用次数以增加 `IO` 效率，`slru`的实现中并不记录每个`buffer page`的 `LSN`，而是记录一组 `page` 的 `LSN`，在刷下一个 `page` 前，需要把一组 `page` 中最大的 `LSN` 前的 `WAL` 落盘。而这样的“一组”的长度，就为`lsn_groups_per_page`

##### 各个进程私有的pointer

```C

/*
 * SlruCtlData is an unshared structure that points to the active information
 * in shared memory.
 */
typedef struct SlruCtlData
{
	SlruShared	shared;

	/*
	 * Decide whether a page is "older" for truncation and as a hint for
	 * evicting pages in LRU order.  
	 */
	bool		(*PagePrecedes) (int, int);

	/*
	 * Dir is set during SimpleLruInit and does not change thereafter. Since
	 * it's always the same, it doesn't need to be in shared memory.
	 */
	char		Dir[64];
} SlruCtlData;
```

初始化时，即返回一个`SlruCtlData`。`Dir` 是初始化时的标记，不同模块会填充对应的名称。


### 核心功能

1. `SimpleLruZeroPage`：新增一个page
2. `SimpleLruReadPage` ：读一个page
3. `SimpleLruWritePage` ：写一个page

#### 基础函数

* 选择一个空slot

```C
/* Select the slot to re-use when we need a free slot. */
/* Control lock must be held at entry, and will be held at exit. */
static int
SlruSelectLRUPage(SlruCtl ctl, int pageno)
{
	for (;;)
		# return if we have such a slot
		# return if we have an empty slot "SLRU_PAGE_EMPTY"
		# select a lru slot
			# return it if it's clean. Or
			# victim it if dirty
	# loop end -- It's a very clever design to dealing with corner cases
	#             such as the victim page being re-dirtied while we wrote it.
}
```

* 记录一个"most recently used"的page，`cur_lru_count++` 并用其赋值 

```C
#define SlruRecentlyUsed(shared, slotno)	\
	do { \
		int		new_lru_count = (shared)->cur_lru_count; \
		if (new_lru_count != (shared)->page_lru_count[slotno]) { \
			(shared)->cur_lru_count = ++new_lru_count; \
			(shared)->page_lru_count[slotno] = new_lru_count; \
		} \
	} while (0)
```

* 从磁盘中读取一个 `page`

```C
SlruPhysicalReadPage
{
    int	segno = pageno / SLRU_PAGES_PER_SEGMENT;
    SlruFileName(ctl, path, segno);

    /*
     * In a crash-and-restart situation, it's possible for us to receive
     * commands to set the commit status of transactions whose bits are in
     * already-truncated segments of the commit log
     */
    fd = OpenTransientFile(path, O_RDONLY | PG_BINARY);
    if (fd < 0 && !InRecovery) ereport()

    pg_pread(fd, shared->page_buffer[slotno], BLCKSZ, offset)
}
```

* 向磁盘中写入一个 `page`

```C
SlruPhysicalWritePage
{
    /* We must flush WAL before flush slru pages */
    if (shared->group_lsn != NULL)
    {
        max_lsn = shared->group_lsn[lsnindex++];
        XLogFlush(max_lsn);
    }

    SlruFileName(ctl, path, segno);
    fd = OpenTransientFile(path, O_RDWR | O_CREAT | PG_BINARY);
    pg_pwrite(fd, shared->page_buffer[slotno], BLCKSZ, offset)
    /* Queue up a sync request for the checkpointer. */
    ...
}
```

#### interface

* 新增一个 `page` 到buffer。
```C
/* Initialize (or reinitialize) a page to zeroes. */
int
SimpleLruZeroPage(SlruCtl ctl, int pageno)
{
	slotno = SlruSelectLRUPage(ctl, pageno);
	SlruRecentlyUsed(shared, slotno);

	# SlruSelectLRUPage may return a in-use page, we must clear it
	MemSet(shared->page_buffer[slotno], 0, BLCKSZ);

	SimpleLruZeroLSNs(ctl, slotno);
}
```

* 从 `disk` 中读取一个 `page`
```C
/* Control lock must be held at entry, and will be held at exit. */
SimpleLruReadPage
{
    #infinite loop
        slotno = SlruSelectLRUPage(ctl, pageno);
        # for in IO slots, just wait
        /* update in-memory status */
        shared->page_number[slotno] = pageno;
        shared->page_status[slotno] = SLRU_PAGE_READ_IN_PROGRESS;
        shared->page_dirty[slotno] = false;

        /* Acquire per-buffer lock and release control lock */
        LWLockAcquire(&shared->buffer_locks[slotno].lock, LW_EXCLUSIVE);
        LWLockRelease(shared->ControlLock);

        ok = SlruPhysicalReadPage(ctl, pageno, slotno);

        /* re-acquire control lock */
        LWLockAcquire(shared->ControlLock, LW_EXCLUSIVE);
        # others
}
```
这里的锁设计很特别：
1. 在 `SlruSelectLRUPage` 需要获取全局锁
2. 在 `SimpleLruReadPage` 中，先初始化内存，再获取 `per-buffer` 锁，同时释放 `ControlLock`

在看函数 `SimpleLruZeroPage`
```C
/* Control lock must be held at entry, and will be held at exit. */
SimpleLruZeroPage
{
    slotno = SlruSelectLRUPage(ctl, pageno);
    shared->page_number[slotno] = pageno;
    shared->page_status[slotno] = SLRU_PAGE_VALID;
    shared->page_dirty[slotno] = true;
}
```
难道，一旦获取 `ControlLock`，即可对任意 `slot` 进行修改？

实际上，`SimpleLruReadPage` 读取的 `page`，必须已存在于磁盘（或者经由 `WAL` 来保证）。
而 `SimpleLruZeroPage` 所初始化的 `page` 必须不存在。从使用逻辑上保证二者不产生冲突。

* SimpleLruWritePage(SlruInternalWritePage)

```C
/* Control lock must be held at entry, and will be held at exit. */
SlruInternalWritePage
{
    /* If a write is in progress, wait for it to finish */
    /* Do nothing if page is not dirty */

    /* update in-memory status */
    shared->page_status[slotno] = SLRU_PAGE_WRITE_IN_PROGRESS;
    shared->page_dirty[slotno] = false;

    /* Acquire per-buffer lock and release control lock */
    LWLockAcquire(&shared->buffer_locks[slotno].lock, LW_EXCLUSIVE);
    LWLockRelease(shared->ControlLock);

    SlruPhysicalWritePage(ctl, pageno, slotno, fdata);

    /* re-acquire control lock */
    LWLockAcquire(shared->ControlLock, LW_EXCLUSIVE);

    shared->page_status[slotno] = SLRU_PAGE_VALID;
}
```
