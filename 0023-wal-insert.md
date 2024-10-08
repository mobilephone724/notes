---
title: WAL日志的插入
author: mobilephone724
math: true
prev: /database/wal/basic
---

## 接口函数

一个WAL记录包含
1. WAL记录类型。（TODO不同的修改有不同的记录方式？）
2. 这个页的修改方式
3. 被修改的页的信息。被修改的页通过一个唯一ID标识，也可以有更多的关联数据（"record-specific data associated with the block"）。如果要写full page，就没有关联数据

### 构建一个WAL记录包含5个核心函数
* `void XLogBeginInsert(void)`
    * 初始化相关状态
    * 如果当前无法构建WAL日志（例如在recovery模式），则报错
* `void XLogRegisterBuffer(uint8 block_id, Buffer buf, uint8 flags);`
    * 增加了数据块的信息；注册一个buffer的引用，相当于上述WAL日志的第三部分
    * > block_id is an arbitrary number used to identify this page reference in the redo routine
    * 在redo阶段，可以根据这些信息找到需要redo的page
```
    regbuf = &registered_buffers[block_id];
    /*
     * Returns the relfilenode, fork number and block number associated with
     * a buffer
     */
    BufferGetTag(buffer, &regbuf->rnode, &regbuf->forkno, &regbuf->block);
    regbuf->page = BufferGetPage(buffer);
    regbuf->flags = flags;
    regbuf->rdata_tail = (XLogRecData *) &regbuf->rdata_head;
    regbuf->rdata_len = 0;
```

registered_buffer的结构
```C
typedef struct
{
    /* xxx */

    /* info to re-find the page */
	ForkNumber	forkno;
	BlockNumber block;
	Page		page;

    /* a loop-linked structure to store the data change of each buffer */
    uint32       rdata_len;      /* total length of data in rdata chain */
    XLogRecData *rdata_head;    /* head of the chain of data registered with
                                * this block */
    XLogRecData *rdata_tail;	/* last entry in the chain, or &rdata_head if
                                 * empty */

    /* xxx */

} registered_buffer;

typedef struct XLogRecData
{
    struct XLogRecData *next;   /* next struct in chain, or NULL */
    char       *data;           /* start of rmgr data to include */
    uint32      len;            /* length of rmgr data to include */
} XLogRecData;
```
* `void XLogRegisterData(char *data, int len);`
    * 向WAL日志中写入任意数据
    * 可多次调用，保证连续。这样在rodo时，就可以得到连续的数据
```C
    rdata = &rdatas[num_rdatas++];
    rdata->data = data;
    rdata->len = len;
```
* `void XLogRegisterBufData(uint8 block_id, char *data, int len);`
```
    rdata = &rdatas[num_rdatas++];
    rdata->data = data;
    rdata->len = len;

    regbuf = &registered_buffers[block_id];
    regbuf->rdata_tail->next = rdata;
    regbuf->rdata_tail = rdata;
    regbuf->rdata_len += len;
```
可见，`XLogRegisterBufData` 和 `XLogRegisterData` 的核心区别在，前者写入的数据会关联到具体的buffer，而后者没有
* `XLogInsert`
  * Insert the record.
```C
    do
    {
        GetFullPageWriteInfo(&RedoRecPtr, &doPageWrites);
        rdt = XLogRecordAssemble(rmid, info, RedoRecPtr, doPageWrites,
                                 &fpw_lsn, &num_fpi);

        EndPos = XLogInsertRecord(rdt, fpw_lsn, curinsert_flags, num_fpi);
	} while (EndPos == InvalidXLogRecPtr);
```

## 数据结构汇总
### registered_buffers
每一个buffer对应registered_buffers中的一个元素（一个`registered buffer`）
```C
void
XLogEnsureRecordSpace(int max_block_id, int ndatas)
{
    if (nbuffers > max_registered_buffers)
    {
        registered_buffers = (registered_buffer *)
            repalloc(registered_buffers, sizeof(registered_buffer) * nbuffers);
        max_registered_buffers = nbuffers;
    }
}
```

## 具体的插入方式
上述代码中的`XLogRecordAssemble`和`XLogInsertRecord`已经概括了具体的插入步骤
### XLogRecordAssemble
> Assemble a WAL record from the registered data and buffers into an XLogRecData chain
```C
static XLogRecData *
XLogRecordAssemble(RmgrId rmid, uint8 info,
				   XLogRecPtr RedoRecPtr, bool doPageWrites,
				   XLogRecPtr *fpw_lsn, int *num_fpi)
{
    for (block_id = 0; block_id < max_registered_block_id; block_id++)
    {
        if (needs_data)
        {
            rdt_datas_last->next = regbuf->rdata_head;
        }
    }
}
```
